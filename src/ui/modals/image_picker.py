"""
ImagePicker - 이미지 영역 선택 모달
드래그로 영역 선택 후 템플릿 이미지로 저장
"""

import customtkinter as ctk
from typing import Optional, Tuple, Callable
import tkinter as tk


class ImagePicker(ctk.CTkToplevel):
    """이미지 영역 선택 모달"""

    def __init__(self, parent, vision_engine, on_select: Callable[[str], None]):
        super().__init__(parent)

        self.vision_engine = vision_engine
        self.on_select = on_select

        # 선택 영역
        self.start_pos: Optional[Tuple[int, int]] = None
        self.end_pos: Optional[Tuple[int, int]] = None

        # 창 설정
        self.title('이미지 영역 선택')
        self.attributes('-fullscreen', True)
        self.attributes('-alpha', 0.3)  # 반투명
        self.configure(cursor='crosshair')

        # 스크린샷 캡처
        self._capture_screenshot()

        # 이벤트 바인딩
        self.bind('<Button-1>', self._on_mouse_down)
        self.bind('<B1-Motion>', self._on_mouse_drag)
        self.bind('<ButtonRelease-1>', self._on_mouse_up)
        self.bind('<Escape>', lambda e: self.destroy())

        # 캔버스
        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            cursor='crosshair'
        )
        self.canvas.pack(fill='both', expand=True)

        # 선택 영역 표시용
        self.selection_rect = None

        print('[ImagePicker] Ready. Drag to select region, Esc to cancel')

    def _capture_screenshot(self):
        """스크린샷 캡처"""
        import numpy as np
        from PIL import Image, ImageTk

        # OpenCV 이미지 가져오기
        screenshot_bgr = self.vision_engine.take_screenshot()

        # BGR -> RGB 변환
        screenshot_rgb = screenshot_bgr[:, :, ::-1]

        # PIL Image로 변환
        self.screenshot_pil = Image.fromarray(screenshot_rgb)
        self.screenshot_tk = ImageTk.PhotoImage(self.screenshot_pil)

    def _on_mouse_down(self, event):
        """마우스 다운"""
        self.start_pos = (event.x_root, event.y_root)
        self.end_pos = self.start_pos

    def _on_mouse_drag(self, event):
        """마우스 드래그"""
        if not self.start_pos:
            return

        self.end_pos = (event.x_root, event.y_root)

        # 선택 영역 그리기
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        self.selection_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='red',
            width=2
        )

    def _on_mouse_up(self, event):
        """마우스 업"""
        if not self.start_pos or not self.end_pos:
            return

        x1, y1 = self.start_pos
        x2, y2 = self.end_pos

        # 좌표 정규화
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        width = right - left
        height = bottom - top

        # 최소 크기 확인
        if width < 10 or height < 10:
            print('[ImagePicker] ✗ Region too small')
            self.destroy()
            return

        print(f'[ImagePicker] Selected region: ({left}, {top}, {width}, {height})')

        # 템플릿 저장
        import time
        timestamp = int(time.time() * 1000)
        output_path = f'targets/target-{timestamp}.png'

        self.vision_engine.save_template((left, top, width, height), output_path)

        # 콜백 호출
        self.on_select(output_path)
        self.destroy()
