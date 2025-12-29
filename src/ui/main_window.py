"""
MainWindow - 메인 애플리케이션 창
CustomTkinter 기반 UI
"""

import customtkinter as ctk
from typing import List, Optional, Callable

# 절대 경로 임포트
try:
    from models import ActionBlock, Settings
    from utils import FileManager
    from core import Automation, Player, Recorder
    from vision import VisionEngine
    from ui.components.header import Header
    from ui.components.sidebar import Sidebar
    from ui.components.action_timeline import ActionTimeline
    from ui.components.detail_panel import DetailPanel
except ImportError:
    from ..models import ActionBlock, Settings
    from ..utils import FileManager
    from ..core import Automation, Player, Recorder
    from ..vision import VisionEngine
    from .components.header import Header
    from .components.sidebar import Sidebar
    from .components.action_timeline import ActionTimeline
    from .components.detail_panel import DetailPanel


class MainWindow(ctk.CTk):
    """메인 애플리케이션 창"""

    def __init__(
        self,
        file_manager: FileManager,
        settings: Settings,
        automation: Automation,
        player: Player,
        recorder: Recorder,
        vision_engine: VisionEngine
    ):
        super().__init__()

        self.file_manager = file_manager
        self.settings = settings
        self.automation = automation
        self.player = player
        self.recorder = recorder
        self.vision_engine = vision_engine

        self.current_blocks: List[ActionBlock] = []
        self.selected_block: Optional[ActionBlock] = None

        # Player 콜백 설정
        self.player.on_block_start = self._on_player_block_start
        self.player.on_block_end = self._on_player_block_end
        self.player.on_complete = self._on_player_complete

        # Recorder 콜백 설정
        self.recorder.on_action_recorded = self._on_action_recorded

        # 창 설정
        self.title('AutoMacro Python v2.0')
        self.geometry('1200x800')
        self.minsize(1000, 600)

        # 레이아웃 구성
        self._setup_layout()

        print('[MainWindow] Initialized')

    def _setup_layout(self):
        """레이아웃 구성"""
        # Grid 설정
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 헤더 (상단)
        self.header = Header(
            self,
            on_record=self._on_record,
            on_play=self._on_play,
            on_stop=self._on_stop,
            on_settings=self._on_settings
        )
        self.header.grid(row=0, column=0, columnspan=3, sticky='ew', padx=10, pady=(10, 5))

        # 사이드바 (좌측)
        self.sidebar = Sidebar(
            self,
            on_add_action=self._on_add_action
        )
        self.sidebar.grid(row=1, column=0, sticky='nsew', padx=(10, 5), pady=(5, 10))

        # 액션 타임라인 (중앙)
        self.timeline = ActionTimeline(
            self,
            on_select=self._on_select_block,
            on_delete=self._on_delete_block,
            on_reorder=self._on_reorder_blocks
        )
        self.timeline.grid(row=1, column=1, sticky='nsew', padx=5, pady=(5, 10))

        # 상세 패널 (우측)
        self.detail_panel = DetailPanel(
            self,
            on_update=self._on_update_block
        )
        self.detail_panel.grid(row=1, column=2, sticky='nsew', padx=(5, 10), pady=(5, 10))

        # 열 너비 설정
        self.grid_columnconfigure(0, weight=0, minsize=200)  # 사이드바
        self.grid_columnconfigure(1, weight=2, minsize=400)  # 타임라인
        self.grid_columnconfigure(2, weight=1, minsize=300)  # 상세 패널

    # --- 콜백 핸들러 ---

    def _on_record(self):
        """녹화 시작"""
        if self.recorder.is_recording:
            # 녹화 중지
            recorded_blocks = self.recorder.stop()
            self.current_blocks.extend(recorded_blocks)
            self.timeline.set_blocks(self.current_blocks)
            self.header.set_recording(False)
            print(f'[MainWindow] Recording stopped. {len(recorded_blocks)} actions recorded')
        else:
            # 녹화 시작
            print('[MainWindow] Recording started')
            self.recorder.start()
            self.header.set_recording(True)

    def _on_play(self):
        """재생 시작"""
        if not self.current_blocks:
            print('[MainWindow] ⚠ No actions to play')
            return

        print(f'[MainWindow] Playing {len(self.current_blocks)} actions...')
        self.header.set_playing(True)

        # 별도 스레드에서 재생
        import threading
        thread = threading.Thread(target=lambda: self.player.play(self.current_blocks))
        thread.daemon = True
        thread.start()

    def _on_stop(self):
        """중지"""
        print('[MainWindow] Stop requested')

        if self.recorder.is_recording:
            recorded_blocks = self.recorder.stop()
            self.current_blocks.extend(recorded_blocks)
            self.timeline.set_blocks(self.current_blocks)

        if self.player.is_playing:
            self.player.stop()

        self.header.set_recording(False)
        self.header.set_playing(False)

    def _on_settings(self):
        """설정 열기"""
        print('[MainWindow] Settings opened')
        # TODO: Phase 6에서 SettingsModal 구현

    def _on_add_action(self, action_type: str):
        """액션 추가"""
        print(f'[MainWindow] Add action: {action_type}')

        # 새 블록 생성
        new_block = ActionBlock(
            type=action_type,
            description=f'{action_type} 액션',
            payload={}
        )

        self.current_blocks.append(new_block)
        self.timeline.set_blocks(self.current_blocks)

        # 새 블록 선택
        self._on_select_block(new_block)

    def _on_select_block(self, block: ActionBlock):
        """블록 선택"""
        print(f'[MainWindow] Block selected: {block.type} - {block.description}')
        self.selected_block = block
        self.detail_panel.set_block(block)

    def _on_update_block(self, block: ActionBlock, updates: dict):
        """블록 업데이트"""
        print(f'[MainWindow] Block updated: {block.id}')

        # 블록 정보 업데이트
        for key, value in updates.items():
            if key == 'payload':
                block.payload.update(value)
            else:
                setattr(block, key, value)

        # 타임라인 갱신
        self.timeline.refresh()

    def _on_delete_block(self, block: ActionBlock):
        """블록 삭제"""
        print(f'[MainWindow] Block deleted: {block.id}')

        if block in self.current_blocks:
            self.current_blocks.remove(block)
            self.timeline.set_blocks(self.current_blocks)

            # 선택 해제
            if self.selected_block == block:
                self.selected_block = None
                self.detail_panel.set_block(None)

    def _on_reorder_blocks(self, blocks: List[ActionBlock]):
        """블록 순서 변경"""
        print(f'[MainWindow] Blocks reordered')
        self.current_blocks = blocks

    # --- 공개 메서드 ---

    def load_project(self, file_path: str):
        """프로젝트 로드"""
        blocks = self.file_manager.load_project(file_path)
        if blocks:
            self.current_blocks = blocks
            self.timeline.set_blocks(blocks)
            print(f'[MainWindow] Project loaded: {len(blocks)} blocks')

    def save_project(self, file_path: str):
        """프로젝트 저장"""
        success = self.file_manager.save_project(self.current_blocks, file_path)
        if success:
            print(f'[MainWindow] Project saved: {len(self.current_blocks)} blocks')
        return success

    # --- Player 콜백 ---

    def _on_player_block_start(self, block: ActionBlock):
        """재생: 블록 시작"""
        print(f'[MainWindow] Playing: {block.type} - {block.description}')

    def _on_player_block_end(self, block: ActionBlock, success: bool):
        """재생: 블록 종료"""
        status = '✓' if success else '✗'
        print(f'[MainWindow] {status} {block.type}')

    def _on_player_complete(self):
        """재생: 완료"""
        print('[MainWindow] Playback completed')
        self.header.set_playing(False)

    # --- Recorder 콜백 ---

    def _on_action_recorded(self, block: ActionBlock):
        """녹화: 액션 기록됨"""
        print(f'[MainWindow] Recorded: {block.type} - {block.description}')
        # 실시간 업데이트는 중지 시 일괄 추가
