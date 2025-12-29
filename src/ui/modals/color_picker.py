"""
ColorPicker - 색상 선택 모달
화면의 픽셀 색상 선택
"""

import customtkinter as ctk
from typing import Optional, Tuple, Callable


class ColorPicker(ctk.CTkToplevel):
    """색상 선택 모달"""

    def __init__(self, parent, vision_engine, on_select: Callable[[Tuple[int, int, int]], None]):
        super().__init__(parent)

        self.vision_engine = vision_engine
        self.on_select = on_select
        self.selected_color: Optional[Tuple[int, int, int]] = None

        # 창 설정
        self.title('색상 선택')
        self.geometry('400x300')
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        # 안내 메시지
        label = ctk.CTkLabel(
            self,
            text='마우스를 원하는 색상 위로 이동한 후\nSpace 키를 눌러 색상을 선택하세요',
            font=('맑은 고딕', 14),
            justify='center'
        )
        label.pack(pady=20)

        # 현재 좌표 표시
        self.coord_label = ctk.CTkLabel(
            self,
            text='현재 좌표: (0, 0)',
            font=('맑은 고딕', 12)
        )
        self.coord_label.pack(pady=10)

        # 색상 프레임
        color_frame = ctk.CTkFrame(self, fg_color='transparent')
        color_frame.pack(pady=10)

        # 색상 미리보기
        self.color_preview = ctk.CTkFrame(
            color_frame,
            width=100,
            height=100,
            corner_radius=10,
            border_width=2,
            border_color='white'
        )
        self.color_preview.pack(side='left', padx=20)

        # RGB 값
        rgb_frame = ctk.CTkFrame(color_frame, fg_color='transparent')
        rgb_frame.pack(side='left', padx=20)

        self.rgb_label = ctk.CTkLabel(
            rgb_frame,
            text='RGB: (0, 0, 0)',
            font=('맑은 고딕', 14, 'bold')
        )
        self.rgb_label.pack()

        self.hex_label = ctk.CTkLabel(
            rgb_frame,
            text='HEX: #000000',
            font=('맑은 고딕', 12)
        )
        self.hex_label.pack(pady=5)

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

        # 색상 추적 시작
        self._track_color()

    def _track_color(self):
        """색상 추적"""
        try:
            import pyautogui
            x, y = pyautogui.position()

            # 픽셀 색상 가져오기
            r, g, b = self.vision_engine.get_pixel_color(x, y)

            # UI 업데이트
            self.coord_label.configure(text=f'현재 좌표: ({x}, {y})')
            self.rgb_label.configure(text=f'RGB: ({r}, {g}, {b})')
            self.hex_label.configure(text=f'HEX: #{r:02X}{g:02X}{b:02X}')

            # 색상 미리보기 업데이트
            hex_color = f'#{r:02X}{g:02X}{b:02X}'
            self.color_preview.configure(fg_color=hex_color)

            self.selected_color = (r, g, b)

        except Exception as e:
            print(f'[ColorPicker] Error: {e}')

        # 100ms마다 갱신
        if self.winfo_exists():
            self.after(100, self._track_color)

    def _select_current(self):
        """현재 색상 선택"""
        if self.selected_color:
            r, g, b = self.selected_color
            print(f'[ColorPicker] Selected: RGB({r}, {g}, {b})')
            self.on_select(self.selected_color)
            self.destroy()

    def _cancel(self):
        """취소"""
        print('[ColorPicker] Cancelled')
        self.destroy()
