import pytest
from infra.screen_manager import ScreenManager

def test_detect_monitors():
    """실제 모니터 감지 테스트"""
    manager = ScreenManager()
    screens = manager.get_screens()
    
    assert len(screens) > 0
    
    main_screen = screens[0]
    # 메인 모니터는 항상 (0, 0)에서 시작해야 함
    assert main_screen.x == 0
    assert main_screen.y == 0
    
    print(f"Detected Screens: {screens}")
