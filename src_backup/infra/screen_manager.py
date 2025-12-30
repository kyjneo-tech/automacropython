import mss
from typing import List
from models.screen_info import ScreenInfo
import platform

class ScreenManager:
    def __init__(self):
        self.sct = mss.mss()

    def get_screens(self) -> List[ScreenInfo]:
        """연결된 모든 모니터 정보 반환"""
        screens = []
        # mss.monitors[0]은 전체 화면(All in one)이므로 1번부터 실제 모니터
        for i, monitor in enumerate(self.sct.monitors[1:], start=1):
            
            # Scale Factor 추론 (간이)
            # macOS에서 mss는 물리 해상도를 반환함.
            # 논리 해상도를 알려면 추가 라이브러리가 필요하지만, 
            # 여기서는 mss 데이터를 신뢰하고 일단 1.0으로 둡니다.
            # (추후 AppKit 연동으로 고도화)
            scale = 1.0
            if platform.system() == 'Darwin':
                # 맥은 보통 2.0이지만, mss가 리턴하는 값은 이미 물리픽셀임.
                # 논리 좌표계 제어를 위해선 OS 스케일을 알아야 함.
                # 일단 기본값.
                pass 

            screen = ScreenInfo(
                id=i,
                x=monitor['left'],
                y=monitor['top'],
                width=monitor['width'],
                height=monitor['height'],
                scale_factor=scale
            )
            screens.append(screen)
            
        return screens
