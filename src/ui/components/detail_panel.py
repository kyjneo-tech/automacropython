"""
DetailPanel - 우측 상세 패널
"""

import customtkinter as ctk
from typing import Callable, Optional

try:
    from models import ActionBlock
except ImportError:
    from ...models import ActionBlock


class DetailPanel(ctk.CTkFrame):
    """우측 상세 패널"""

    def __init__(self, parent, on_update: Callable):
        super().__init__(parent, width=300)

        self.on_update = on_update
        self.current_block: Optional[ActionBlock] = None

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        # 제목
        self.title_label = ctk.CTkLabel(
            self,
            text='상세 설정',
            font=('맑은 고딕', 18, 'bold')
        )
        self.title_label.pack(pady=(10, 20))

        # 스크롤 가능 프레임
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # 빈 상태 메시지
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text='액션을 선택하세요',
            font=('맑은 고딕', 14),
            text_color='gray'
        )
        self.empty_label.pack(pady=50)

    def set_block(self, block: Optional[ActionBlock]):
        """블록 설정"""
        self.current_block = block

        # 기존 위젯 제거
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not block:
            self.empty_label = ctk.CTkLabel(
                self.scroll_frame,
                text='액션을 선택하세요',
                font=('맑은 고딕', 14),
                text_color='gray'
            )
            self.empty_label.pack(pady=50)
            return

        # 타입별 설정 UI 생성
        self._create_fields_for_type(block.type)

    def _create_fields_for_type(self, action_type: str):
        """타입별 설정 필드 생성"""
        # 설명 필드 (모든 타입 공통)
        self._add_field('설명', 'description', 'entry')

        # 타입별 필드
        if action_type in ['click', 'dblclick']:
            self._add_field('X 좌표', 'payload.x', 'number')
            self._add_field('Y 좌표', 'payload.y', 'number')
            self._add_field('버튼', 'payload.button', 'choice', ['left', 'right', 'middle'])

        elif action_type == 'drag':
            self._add_field('시작 X', 'payload.start_x', 'number')
            self._add_field('시작 Y', 'payload.start_y', 'number')
            self._add_field('끝 X', 'payload.end_x', 'number')
            self._add_field('끝 Y', 'payload.end_y', 'number')

        elif action_type == 'scroll':
            self._add_field('스크롤 양', 'payload.amount', 'number')

        elif action_type == 'type':
            self._add_field('텍스트', 'payload.text', 'textbox')

        elif action_type == 'shortcut':
            self._add_field('단축키', 'payload.keys', 'entry')

        elif action_type == 'delay':
            self._add_field('시간 (ms)', 'payload.duration', 'number')

        elif action_type == 'condition-image':
            self._add_field('이미지 경로', 'payload.path', 'entry')
            self._add_field('신뢰도', 'payload.confidence', 'slider', (0.5, 1.0))

        elif action_type == 'loop-count':
            self._add_field('반복 횟수', 'payload.count', 'number')
            self._add_field('간격 (ms)', 'payload.delay_between', 'number')

    def _add_field(self, label: str, field_path: str, field_type: str, options=None):
        """필드 추가"""
        # 레이블
        label_widget = ctk.CTkLabel(
            self.scroll_frame,
            text=label,
            font=('맑은 고딕', 12),
            anchor='w'
        )
        label_widget.pack(fill='x', pady=(10, 5))

        # 현재 값 가져오기
        current_value = self._get_field_value(field_path)

        # 필드 타입별 위젯 생성
        if field_type == 'entry':
            widget = ctk.CTkEntry(self.scroll_frame, font=('맑은 고딕', 12))
            widget.insert(0, str(current_value) if current_value else '')
            widget.bind('<KeyRelease>', lambda e: self._update_field(field_path, widget.get()))

        elif field_type == 'number':
            widget = ctk.CTkEntry(self.scroll_frame, font=('맑은 고딕', 12))
            widget.insert(0, str(current_value) if current_value else '0')
            widget.bind('<KeyRelease>', lambda e: self._update_field(field_path, int(widget.get() or 0)))

        elif field_type == 'textbox':
            widget = ctk.CTkTextbox(self.scroll_frame, height=100, font=('맑은 고딕', 12))
            widget.insert('1.0', str(current_value) if current_value else '')
            widget.bind('<KeyRelease>', lambda e: self._update_field(field_path, widget.get('1.0', 'end-1c')))

        elif field_type == 'choice':
            widget = ctk.CTkOptionMenu(
                self.scroll_frame,
                values=options,
                command=lambda v: self._update_field(field_path, v),
                font=('맑은 고딕', 12)
            )
            if current_value in options:
                widget.set(current_value)

        elif field_type == 'slider':
            min_val, max_val = options
            widget = ctk.CTkSlider(
                self.scroll_frame,
                from_=min_val,
                to=max_val,
                command=lambda v: self._update_field(field_path, v)
            )
            widget.set(float(current_value) if current_value else min_val)

        else:
            return

        widget.pack(fill='x', pady=(0, 10))

    def _get_field_value(self, field_path: str):
        """필드 값 가져오기"""
        if not self.current_block:
            return None

        parts = field_path.split('.')
        value = self.current_block

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part, None)

        return value

    def _update_field(self, field_path: str, new_value):
        """필드 값 업데이트"""
        if not self.current_block:
            return

        parts = field_path.split('.')

        if parts[0] == 'payload':
            # payload 필드
            self.current_block.payload[parts[1]] = new_value
            self.on_update(self.current_block, {'payload': {parts[1]: new_value}})
        else:
            # 일반 필드
            setattr(self.current_block, parts[0], new_value)
            self.on_update(self.current_block, {parts[0]: new_value})
