"""
Automation - 기본 자동화 기능 (마우스/키보드)
PyAutoGUI + pyperclip 기반
"""

import pyautogui
import pyperclip
import time
from typing import Tuple, List


class Automation:
    """자동화 실행 엔진"""

    def __init__(self):
        # PyAutoGUI 설정
        pyautogui.PAUSE = 0.05  # 각 명령 후 기본 대기 시간
        pyautogui.FAILSAFE = True  # 마우스를 좌상단으로 이동하면 중단

        print('[Automation] Initialized')

    # --- 마우스 제어 ---

    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1, interval: float = 0.0):
        """
        마우스 클릭

        Args:
            x: X 좌표
            y: Y 좌표
            button: 'left', 'right', 'middle'
            clicks: 클릭 횟수
            interval: 클릭 간격 (초)
        """
        print(f'[Automation] Click: ({x}, {y}) button={button} clicks={clicks}')
        pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)

    def double_click(self, x: int, y: int, button: str = 'left'):
        """더블클릭"""
        print(f'[Automation] Double click: ({x}, {y})')
        pyautogui.doubleClick(x, y, button=button)

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
        """
        드래그

        Args:
            start_x, start_y: 시작 좌표
            end_x, end_y: 끝 좌표
            duration: 드래그 시간 (초)
        """
        print(f'[Automation] Drag: ({start_x}, {start_y}) -> ({end_x}, {end_y})')
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=duration, button='left')

    def move_to(self, x: int, y: int, duration: float = 0.5):
        """마우스 이동"""
        print(f'[Automation] Move to: ({x}, {y})')
        pyautogui.moveTo(x, y, duration=duration)

    def scroll(self, amount: int, x: int = None, y: int = None):
        """
        스크롤

        Args:
            amount: 스크롤 양 (양수: 위로, 음수: 아래로)
            x, y: 스크롤 위치 (None이면 현재 위치)
        """
        print(f'[Automation] Scroll: amount={amount}')
        if x is not None and y is not None:
            pyautogui.moveTo(x, y)
        pyautogui.scroll(amount)

    def repeat_click(self, x: int, y: int, count: int, interval: float = 0.1, button: str = 'left'):
        """
        연타

        Args:
            x, y: 클릭 위치
            count: 클릭 횟수
            interval: 클릭 간격 (초)
            button: 버튼
        """
        print(f'[Automation] Repeat click: ({x}, {y}) count={count} interval={interval}')
        for i in range(count):
            pyautogui.click(x, y, button=button)
            if i < count - 1:
                time.sleep(interval)

    def get_mouse_position(self) -> Tuple[int, int]:
        """현재 마우스 좌표 가져오기"""
        return pyautogui.position()

    # --- 키보드 제어 ---

    def type_text(self, text: str, interval: float = 0.05, use_clipboard: bool = True):
        """
        텍스트 입력

        Args:
            text: 입력할 텍스트
            interval: 키 입력 간격 (초)
            use_clipboard: 클립보드 사용 여부 (한글 입력에 필요)
        """
        print(f'[Automation] Type text: "{text[:50]}..." use_clipboard={use_clipboard}')

        if use_clipboard:
            # 클립보드 사용 (한글 입력)
            original_clipboard = pyperclip.paste()
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyperclip.copy(original_clipboard)
        else:
            # 직접 입력 (영문/숫자만)
            pyautogui.write(text, interval=interval)

    def press_key(self, key: str):
        """
        키 입력

        Args:
            key: 키 이름 ('enter', 'space', 'a', 'shift', etc.)
        """
        print(f'[Automation] Press key: {key}')
        pyautogui.press(key)

    def hotkey(self, *keys: str):
        """
        단축키 입력

        Args:
            keys: 키 조합 ('ctrl', 'c')
        """
        print(f'[Automation] Hotkey: {"+".join(keys)}')
        pyautogui.hotkey(*keys)

    def key_down(self, key: str):
        """키 누름"""
        print(f'[Automation] Key down: {key}')
        pyautogui.keyDown(key)

    def key_up(self, key: str):
        """키 뗌"""
        print(f'[Automation] Key up: {key}')
        pyautogui.keyUp(key)

    def repeat_key(self, key: str, count: int, interval: float = 0.1):
        """
        키 연타

        Args:
            key: 키 이름
            count: 반복 횟수
            interval: 간격 (초)
        """
        print(f'[Automation] Repeat key: {key} count={count} interval={interval}')
        for i in range(count):
            pyautogui.press(key)
            if i < count - 1:
                time.sleep(interval)

    # --- 화면 정보 ---

    def get_screen_size(self) -> Tuple[int, int]:
        """화면 크기 가져오기"""
        return pyautogui.size()

    def screenshot(self, region: Tuple[int, int, int, int] = None):
        """
        스크린샷

        Args:
            region: (left, top, width, height) 영역 (None이면 전체 화면)

        Returns:
            PIL Image 객체
        """
        return pyautogui.screenshot(region=region)

    # --- 대기 ---

    def delay(self, duration: float):
        """
        대기

        Args:
            duration: 대기 시간 (초)
        """
        print(f'[Automation] Delay: {duration}s')
        time.sleep(duration)
