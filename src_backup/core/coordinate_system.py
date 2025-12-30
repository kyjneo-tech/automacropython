from typing import List, Tuple
from models.screen_info import ScreenInfo

class CoordinateSystem:
    def __init__(self, screens: List[ScreenInfo]):
        self.screens = sorted(screens, key=lambda s: s.x) # X축 순 정렬

    def to_physical(self, logical_x: int, logical_y: int) -> Tuple[int, int]:
        """논리 좌표(포인트)를 물리 좌표(픽셀)로 변환"""
        
        # 1. 어떤 스크린에 속해 있는지 찾기
        target_screen = None
        for screen in self.screens:
            if (screen.x <= logical_x < screen.x + screen.width and
                screen.y <= logical_y < screen.y + screen.height):
                target_screen = screen
                break
        
        # 화면 밖이면 기본 변환 (그냥 스케일만 곱함 - 예외처리)
        if not target_screen:
            # 가장 가까운 스크린을 찾거나, 기본 1번 스크린 기준
            target_screen = self.screens[0]

        # 2. 해당 스크린 내에서의 상대 좌표 계산
        rel_x = logical_x - target_screen.x
        rel_y = logical_y - target_screen.y

        # 3. 스케일 적용 (물리적 상대 좌표)
        phy_rel_x = int(rel_x * target_screen.scale_factor)
        phy_rel_y = int(rel_y * target_screen.scale_factor)

        # 4. 물리적 절대 좌표 계산 (이전 스크린들의 물리 너비 합산)
        # 중요: OpenCV mss 캡처는 물리 픽셀을 순서대로 붙여서 가져옴.
        # 따라서 내 앞쪽에 있는 모니터들의 '물리적 너비'를 다 더해야 함.
        phy_offset_x = 0
        phy_offset_y = 0 # Y축 정렬은 일단 무시 (가로 배치 가정) -> 나중에 고도화 필요

        for screen in self.screens:
            if screen == target_screen:
                phy_offset_y = int(target_screen.y * target_screen.scale_factor) # Y 오프셋도 스케일 적용
                break
            phy_offset_x += screen.physical_width

        return (phy_offset_x + phy_rel_x, phy_offset_y + phy_rel_y)
