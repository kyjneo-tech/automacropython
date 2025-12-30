from src.domain.coordinate import CoordinateTransformer, ScreenInfo

def test_monitor_scaling():
    """
    Test 1: Retina Display Scaling
    Logical Resolution: 1280x800
    Physical Resolution: 2560x1600
    Scale Factor: 2.0
    
    Given: Logical Point (500, 500)
    Expected: Physical coordinates on Screen 0 -> (1000, 1000)
    """
    # Arrange
    screens = [ScreenInfo(x=0, y=0, width=1280, height=800, scale_factor=2.0)]
    transformer = CoordinateTransformer(screens)
    
    # Act
    # Retrieve the screen index and local pixel coordinates
    screen_idx, phys_x, phys_y = transformer.to_physical_local(500, 500)
    
    # Assert
    assert screen_idx == 0
    assert phys_x == 1000
    assert phys_y == 1000

def test_dual_monitor_offset():
    """
    Test 2: Dual Monitor Setup
    Monitor 1 (Main): 1920x1080, Scale 1.0, Pos (0,0)
    Monitor 2 (Sub): 1920x1080, Scale 1.0, Pos (1920, 0)
    
    Given: Logical Point (2020, 100) -> on Monitor 2
    Expected: Screen 1, Local Pixel (100, 100)
    """
    # Arrange
    screens = [
        ScreenInfo(x=0, y=0, width=1920, height=1080, scale_factor=1.0),
        ScreenInfo(x=1920, y=0, width=1920, height=1080, scale_factor=1.0)
    ]
    transformer = CoordinateTransformer(screens)
    
    # Act
    # x=2020 is 100px into the second monitor (index 1)
    screen_idx, phys_x, phys_y = transformer.to_physical_local(2020, 100)
    
    # Assert
    assert screen_idx == 1
    assert phys_x == 100 # 2020 - 1920 = 100
    assert phys_y == 100

def test_mixed_dpi_setup():
    """
    Test 3: Mixed DPI Setup (The Killer Case)
    Monitor 1 (Retina): 1440x900 (Logical), Scale 2.0, Pos (0,0)
    Monitor 2 (Normal): 1920x1080 (Logical), Scale 1.0, Pos (1440, 0)
    
    Scenario: User clicks on Monitor 2 at logical (1540, 100)
    (1540 is 100px inside Monitor 2)
    
    Monitor 1 Physical Width = 1440 * 2 = 2880
    Monitor 2 starts at Logical x=1440.
    
    Wait, how does MacOS handle "Physical" coordinates across mixed displays?
    It doesn't strictly have a continuous "Physical" coordinate system if pixel densities differ.
    However, for mouse events (CGEventPost), we usually use "Points" (Logical Coordinates).
    
    BUT, if we are doing Image Matching (OpenCV), we grab a screenshot in PIXELS.
    So we need to convert: 
    Image Match Found at Pixel (Screen 2 Local Pixel x=100, y=100)
    -> Global Logical Coordinate (for Mouse Click).
    
    Let's reverse the test: Physical (Image Find) -> Logical (Mouse Click).
    
    Case: Match found on Screen 2.
    Screen 2 Physical Offset (in theoretical global pixel space? No, usually separate framebuffers).
    We treat each screen as having its own pixel space for image search.
    
    Let's assume the Vision module returns: (ScreenIndex, Pixel_X, Pixel_Y).
    We need to convert that to Global Logical (Point_X, Point_Y).
    """
    # Arrange
    screens = [
        ScreenInfo(x=0, y=0, width=1440, height=900, scale_factor=2.0), # Screen 0
        ScreenInfo(x=1440, y=0, width=1920, height=1080, scale_factor=1.0) # Screen 1
    ]
    transformer = CoordinateTransformer(screens)
    
    # Act 1: Retina Screen (Screen 0)
    # Found image at Pixel (500, 500) on Screen 0
    log_x, log_y = transformer.to_logical(screen_index=0, pixel_x=500, pixel_y=500)
    
    # Assert 1: 500px / 2.0 = 250pt
    assert log_x == 250
    assert log_y == 250
    
    # Act 2: Normal Screen (Screen 1)
    # Found image at Pixel (100, 100) on Screen 1
    log_x2, log_y2 = transformer.to_logical(screen_index=1, pixel_x=100, pixel_y=100)
    
    # Assert 2: 
    # Global Logical X = Screen 1 Origin (1440) + (100px / 1.0)
    assert log_x2 == 1440 + 100
    assert log_y2 == 0 + 100 # y is aligned at 0
