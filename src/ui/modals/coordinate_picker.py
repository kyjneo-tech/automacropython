"""
CoordinatePicker - 좌표 선택 모달
화면을 클릭하여 좌표 선택
"""

import customtkinter as ctk
from typing import Optional, Tuple, Callable
import time

# pyautogui 임포트 확인
try:
    import pyautogui
except ImportError:
    pyautogui = None


class CoordinatePicker(ctk.CTkToplevel):
    """좌표 선택 모달"""

    def __init__(self, parent, on_select: Callable[[int, int], None]):
        super().__init__(parent)

        self.on_select = on_select
        self.selected_pos: Optional[Tuple[int, int]] = None

        # 창 설정
        self.title('좌표 선택')
        self.geometry('400x200')
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        # 안내 메시지
        label = ctk.CTkLabel(
            self,
            text='마우스를 원하는 위치로 이동한 후\nSpace 키를 눌러 좌표를 선택하세요',
            font=('맑은 고딕', 14),
            justify='center'
        )
        label.pack(pady=30)

        # 현재 좌표 표시
        self.coord_label = ctk.CTkLabel(
            self,
            text='현재 좌표: (0, 0)',
            font=('맑은 고딕', 16, 'bold')
        )
        self.coord_label.pack(pady=20)

        # 버튼 프레임
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.pack(pady=20)

        # 선택 버튼
        select_btn = ctk.CTkButton(
            btn_frame,
            text='선택 (Space)',
            command=self._select_current,
            width=120,
            font=('맑은 고딕', 12)
        )
        select_btn.pack(side='left', padx=5)

        # 취소 버튼
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text='취소 (Esc)',
            command=self._cancel,
            width=120,
            font=('맑은 고딕', 12),
            fg_color='gray'
        )
        cancel_btn.pack(side='left', padx=5)

        # 키보드 바인딩
        self.bind('<space>', lambda e: self._select_current())
        self.bind('<Escape>', lambda e: self._cancel())

        # 좌표 추적 시작
        self._track_mouse()

    def _track_mouse(self):
        """마우스 좌표 추적"""
        if pyautogui:
            try:
                x, y = pyautogui.position()
                self.coord_label.configure(text=f'현재 좌표: ({x}, {y})')
                self.selected_pos = (x, y)
            except:
                pass

        # 100ms마다 갱신
        if self.winfo_exists():
            self.after(100, self._track_mouse)

    def _select_current(self):
        """현재 좌표 선택"""
        if self.selected_pos:
            x, y = self.selected_pos
            print(f'[CoordinatePicker] Selected: ({x}, {y})')
            self.on_select(x, y)
            self.destroy()

    def _cancel(self):
        """취소"""
        print('[CoordinatePicker] Cancelled')
        self.destroy()
