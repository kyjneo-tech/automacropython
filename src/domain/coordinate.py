from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class ScreenInfo:
    x: int
    y: int
    width: int
    height: int
    scale_factor: float
    
    @property
    def logical_right(self):
        return self.x + self.width
        
    @property
    def logical_bottom(self):
        return self.y + self.height

class CoordinateTransformer:
    def __init__(self, screens: List[ScreenInfo]):
        self.screens = screens

    def to_physical_local(self, logical_x: int, logical_y: int) -> Tuple[int, int, int]:
        """
        Convert Global Logical Point to (ScreenIndex, LocalPixelX, LocalPixelY).
        This is used for determining which screen to capture and where.
        """
        # Find the screen containing the point
        target_idx = -1
        target_screen = None
        
        for idx, screen in enumerate(self.screens):
            if (screen.x <= logical_x < screen.logical_right and 
                screen.y <= logical_y < screen.logical_bottom):
                target_idx = idx
                target_screen = screen
                break
        
        if target_screen is None:
            # Fallback to primary screen (0) if out of bounds
            # Or clamp? Let's fallback to 0 for safety, or raise error.
            # Given WYSIWYG, maybe clamping is better?
            # Let's fallback to 0.
            target_idx = 0
            target_screen = self.screens[0]

        # Calculate local offset from screen origin
        local_log_x = logical_x - target_screen.x
        local_log_y = logical_y - target_screen.y
        
        # Convert to local physical
        local_phys_x = int(local_log_x * target_screen.scale_factor)
        local_phys_y = int(local_log_y * target_screen.scale_factor)
        
        return (target_idx, local_phys_x, local_phys_y)

    def _find_screen_containing(self, log_x, log_y) -> Optional[ScreenInfo]:
        for idx, screen in enumerate(self.screens):
            if (screen.x <= log_x < screen.logical_right and 
                screen.y <= log_y < screen.logical_bottom):
                return screen
        return None

    def to_logical(self, screen_index: int, pixel_x: int, pixel_y: int) -> Tuple[int, int]:
        """
        Convert Local Physical Pixel on specific screen to Global Logical Point.
        """
        if screen_index >= len(self.screens):
            return (0, 0) # Error
            
        screen = self.screens[screen_index]
        
        # Local Physical -> Local Logical
        local_log_x = pixel_x / screen.scale_factor
        local_log_y = pixel_y / screen.scale_factor
        
        # Local Logical -> Global Logical
        global_log_x = screen.x + local_log_x
        global_log_y = screen.y + local_log_y
        
        return (int(global_log_x), int(global_log_y))
