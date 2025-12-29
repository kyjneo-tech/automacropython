"""
Sidebar - 좌측 도구 사이드바
"""

import customtkinter as ctk
from typing import Callable

try:
    from models.action_block import ActionType
except ImportError:
    from ...models.action_block import ActionType


class Sidebar(ctk.CTkFrame):
    """좌측 도구 사이드바"""

    def __init__(self, parent, on_add_action: Callable):
        super().__init__(parent, width=200)

        self.on_add_action = on_add_action
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        # 제목
        title_label = ctk.CTkLabel(
            self,
            text='도구',
            font=('맑은 고딕', 18, 'bold')
        )
        title_label.pack(pady=(10, 20))

        # 스크롤 가능 프레임
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color='transparent')
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # 카테고리별 액션
        self._add_category(scroll_frame, '🖱️ 마우스', [
            ('클릭', ActionType.CLICK),
            ('더블클릭', ActionType.DOUBLE_CLICK),
            ('드래그', ActionType.DRAG),
            ('스크롤', ActionType.SCROLL),
            ('연타', ActionType.REPEAT_CLICK)
        ])

        self._add_category(scroll_frame, '⌨️ 키보드', [
            ('텍스트 입력', ActionType.TYPE),
            ('단축키', ActionType.SHORTCUT),
            ('키 연타', ActionType.KEY_REPEAT)
        ])

        self._add_category(scroll_frame, '⏱️ 흐름 제어', [
            ('대기', ActionType.DELAY),
            ('이미지 조건', ActionType.CONDITION_IMAGE),
            ('루프', ActionType.LOOP_COUNT)
        ])

        self._add_category(scroll_frame, '🔧 고급', [
            ('변수 설정', ActionType.VARIABLE_SET),
            ('이미지 대기', ActionType.WAIT_UNTIL_IMAGE),
            ('색상 대기', ActionType.WAIT_UNTIL_COLOR)
        ])

    def _add_category(self, parent, title: str, actions: list):
        """카테고리 추가"""
        # 카테고리 제목
        category_label = ctk.CTkLabel(
            parent,
            text=title,
            font=('맑은 고딕', 14, 'bold'),
            anchor='w'
        )
        category_label.pack(fill='x', pady=(10, 5))

        # 액션 버튼들
        for label, action_type in actions:
            btn = ctk.CTkButton(
                parent,
                text=label,
                command=lambda at=action_type: self.on_add_action(at),
                height=32,
                font=('맑은 고딕', 12),
                anchor='w'
            )
            btn.pack(fill='x', pady=2)
