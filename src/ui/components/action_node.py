"""
ActionNode - 개별 액션 블록 카드
"""

import customtkinter as ctk
from typing import Callable

try:
    from models import ActionBlock
except ImportError:
    from ...models import ActionBlock


class ActionNode(ctk.CTkFrame):
    """개별 액션 블록 UI"""

    def __init__(self, parent, block: ActionBlock, index: int, on_select: Callable, on_delete: Callable):
        super().__init__(parent, corner_radius=10)

        self.block = block
        self.index = index
        self.on_select = on_select
        self.on_delete = on_delete
        self.is_selected = False

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        self.configure(fg_color=('#E0E0E0', '#2B2B2B'))

        # 좌측: 번호 + 아이콘
        left_frame = ctk.CTkFrame(self, fg_color='transparent')
        left_frame.pack(side='left', padx=10, pady=10)

        index_label = ctk.CTkLabel(
            left_frame,
            text=f'{self.index}.',
            font=('맑은 고딕', 16, 'bold'),
            width=30
        )
        index_label.pack()

        # 중앙: 타입 + 설명
        center_frame = ctk.CTkFrame(self, fg_color='transparent')
        center_frame.pack(side='left', fill='both', expand=True, padx=5, pady=10)

        type_label = ctk.CTkLabel(
            center_frame,
            text=self._get_type_icon() + ' ' + self._get_type_text(),
            font=('맑은 고딕', 14, 'bold'),
            anchor='w'
        )
        type_label.pack(fill='x')

        desc_label = ctk.CTkLabel(
            center_frame,
            text=self.block.description or self._get_default_description(),
            font=('맑은 고딕', 12),
            anchor='w',
            text_color='gray'
        )
        desc_label.pack(fill='x')

        # 우측: 삭제 버튼
        delete_btn = ctk.CTkButton(
            self,
            text='🗑️',
            command=lambda: self.on_delete(),
            width=40,
            fg_color='#C94C4C',
            hover_color='#A03C3C'
        )
        delete_btn.pack(side='right', padx=10, pady=10)

        # 클릭 이벤트
        self.bind('<Button-1>', lambda e: self.on_select())
        for widget in [left_frame, center_frame, index_label, type_label, desc_label]:
            widget.bind('<Button-1>', lambda e: self.on_select())

    def _get_type_icon(self) -> str:
        """타입별 아이콘"""
        icons = {
            'click': '🖱️',
            'dblclick': '🖱️',
            'drag': '🖱️',
            'scroll': '🖱️',
            'repeat-click': '🖱️',
            'type': '⌨️',
            'shortcut': '⌨️',
            'key-repeat': '⌨️',
            'delay': '⏱️',
            'condition-image': '🔍',
            'loop-count': '🔁',
            'variable-set': '📝',
            'wait-until-image': '⏳',
            'wait-until-color': '⏳'
        }
        return icons.get(self.block.type, '📦')

    def _get_type_text(self) -> str:
        """타입별 텍스트"""
        texts = {
            'click': '클릭',
            'dblclick': '더블클릭',
            'drag': '드래그',
            'scroll': '스크롤',
            'repeat-click': '연타',
            'type': '텍스트 입력',
            'shortcut': '단축키',
            'key-repeat': '키 연타',
            'delay': '대기',
            'condition-image': '이미지 조건',
            'loop-count': '루프',
            'variable-set': '변수 설정',
            'wait-until-image': '이미지 대기',
            'wait-until-color': '색상 대기'
        }
        return texts.get(self.block.type, self.block.type)

    def _get_default_description(self) -> str:
        """기본 설명"""
        payload = self.block.payload

        if self.block.type == 'click':
            return f"({payload.get('x', 0)}, {payload.get('y', 0)}) 클릭"
        elif self.block.type == 'delay':
            duration = payload.get('duration', 0) / 1000
            return f"{duration}초 대기"
        elif self.block.type == 'type':
            text = payload.get('text', '')[:20]
            return f'"{text}..." 입력'
        else:
            return '설정 필요'

    def set_selected(self, selected: bool):
        """선택 상태 설정"""
        self.is_selected = selected

        if selected:
            self.configure(fg_color=('#3B8ED0', '#1F6AA5'), border_width=2, border_color='white')
        else:
            self.configure(fg_color=('#E0E0E0', '#2B2B2B'), border_width=0)
