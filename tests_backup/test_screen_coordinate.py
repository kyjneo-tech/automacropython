import pytest
from dataclasses import dataclass

# 아직 만들지 않은 모듈 (에러 예정)
from core.coordinate_system import CoordinateSystem
from models.screen_info import ScreenInfo

def test_single_monitor_retina_conversion():
    """레티나 디스플레이(2x)에서 논리 좌표 -> 물리 좌표 변환 테스트"""
    # 1. 화면 설정 (1920x1080, Scale 2.0)
    screen = ScreenInfo(id=0, x=0, y=0, width=1920, height=1080, scale_factor=2.0)
    coord_sys = CoordinateSystem([screen])

    # 2. (100, 100) 클릭 요청
    # 레티나(macOS)에서는 논리좌표 100이 물리좌표 200일 수 있고, 
    # 혹은 OS가 자동으로 처리해줘서 100일 수도 있음.
    # 하지만 여기서는 'Scale Factor를 고려한 정확한 픽셀 매핑'을 검증.
    # 만약 pyautogui가 논리좌표를 받는다면 그대로 100이어야 하고,
    # OpenCV가 물리좌표(캡처본)를 쓴다면 200이어야 함.
    # **AutoFlow X 정책: 내부 로직은 항상 '물리 좌표(Pixel)' 기준**
    
    physical_pos = coord_sys.to_physical(100, 100)
    assert physical_pos == (200, 200)

def test_dual_monitor_conversion():
    """듀얼 모니터(Main: Retina, Sub: Normal) 좌표 변환 테스트"""
    # Main: 0~1920 (Scale 2.0)
    # Sub: 1920~3840 (Scale 1.0)
    main_screen = ScreenInfo(id=0, x=0, y=0, width=1920, height=1080, scale_factor=2.0)
    sub_screen = ScreenInfo(id=1, x=1920, y=0, width=1920, height=1080, scale_factor=1.0)
    
    coord_sys = CoordinateSystem([main_screen, sub_screen])

    # Case A: 메인 모니터 (100, 100) -> 물리 (200, 200)
    assert coord_sys.to_physical(100, 100) == (200, 200)

    # Case B: 서브 모니터 (2020, 100) -> 
    # 논리적으로 2020은 메인(1920)을 지나 서브의 100 지점.
    # 메인 물리 너비 = 1920 * 2 = 3840
    # 서브 물리 오프셋 = 3840
    # 서브 내 상대 위치 = 100 * 1.0 = 100
    # 결과 = 3840 + 100 = 3940
    # Y좌표는 Top-Align 가정 시 서브(Scale 1.0)는 그대로 100
    assert coord_sys.to_physical(2020, 100) == (3940, 100)
