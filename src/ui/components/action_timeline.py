"""
ActionTimeline - 중앙 액션 타임라인
"""

import customtkinter as ctk
from typing import List, Callable, Optional

try:
    from models import ActionBlock
    from ui.components.action_node import ActionNode
except ImportError:
    from ...models import ActionBlock
    from .action_node import ActionNode


class ActionTimeline(ctk.CTkFrame):
    """액션 타임라인"""

    def __init__(self, parent, on_select: Callable, on_delete: Callable, on_reorder: Callable):
        super().__init__(parent)

        self.on_select = on_select
        self.on_delete = on_delete
        self.on_reorder = on_reorder

        self.blocks: List[ActionBlock] = []
        self.nodes: List[ActionNode] = []
        self.selected_node: Optional[ActionNode] = None

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        # 제목
        title_label = ctk.CTkLabel(
            self,
            text='액션 타임라인',
            font=('맑은 고딕', 18, 'bold')
        )
        title_label.pack(pady=(10, 10))

        # 스크롤 가능 프레임
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # 빈 상태 메시지
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text='좌측에서 액션을 추가하세요',
            font=('맑은 고딕', 14),
            text_color='gray'
        )
        self.empty_label.pack(pady=50)

    def set_blocks(self, blocks: List[ActionBlock]):
        """블록 목록 설정"""
        self.blocks = blocks
        self.refresh()

    def refresh(self):
        """타임라인 새로고침"""
        # 기존 노드 제거
        for node in self.nodes:
            node.destroy()
        self.nodes.clear()

        # 빈 상태 처리
        if not self.blocks:
            self.empty_label.pack(pady=50)
            return
        else:
            self.empty_label.pack_forget()

        # 새 노드 생성
        for i, block in enumerate(self.blocks):
            node = ActionNode(
                self.scroll_frame,
                block,
                index=i + 1,
                on_select=lambda b=block: self._on_node_selected(b),
                on_delete=lambda b=block: self._on_node_deleted(b)
            )
            node.pack(fill='x', pady=5)
            self.nodes.append(node)

    def _on_node_selected(self, block: ActionBlock):
        """노드 선택"""
        # 이전 선택 해제
        if self.selected_node:
            self.selected_node.set_selected(False)

        # 새 노드 선택
        for node in self.nodes:
            if node.block == block:
                node.set_selected(True)
                self.selected_node = node
                break

        self.on_select(block)

    def _on_node_deleted(self, block: ActionBlock):
        """노드 삭제"""
        self.on_delete(block)
