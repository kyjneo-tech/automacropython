"""
Player - 액션 블록 재생 엔진
"""

import time
from typing import List, Callable, Optional, Dict, Any

try:
    from models import ActionBlock, ActionStatus
    from core.automation import Automation
except ImportError:
    from ..models import ActionBlock, ActionStatus
    from .automation import Automation


class Player:
    """액션 재생 엔진"""

    def __init__(self, automation: Automation):
        self.automation = automation
        self.is_playing = False
        self.is_paused = False
        self.should_stop = False

        # 콜백
        self.on_block_start: Optional[Callable[[ActionBlock], None]] = None
        self.on_block_end: Optional[Callable[[ActionBlock, bool], None]] = None
        self.on_complete: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None

        # 변수 저장소 (Phase 8)
        self.variables: Dict[str, Any] = {}

        print('[Player] Initialized')

    def play(self, blocks: List[ActionBlock], loop: bool = False):
        """
        액션 블록 재생

        Args:
            blocks: 재생할 블록 리스트
            loop: 루프 재생 여부
        """
        print(f'[Player] Starting playback ({len(blocks)} blocks, loop={loop})')

        self.is_playing = True
        self.should_stop = False

        try:
            while True:
                for block in blocks:
                    if self.should_stop:
                        print('[Player] Stopped by user')
                        return

                    # 일시정지 대기
                    while self.is_paused and not self.should_stop:
                        time.sleep(0.1)

                    if self.should_stop:
                        return

                    # 블록 실행
                    self._execute_block(block)

                # 루프가 아니면 종료
                if not loop:
                    break

        except Exception as e:
            print(f'[Player] Error: {e}')
            if self.on_error:
                self.on_error(e)

        finally:
            self.is_playing = False
            if self.on_complete:
                self.on_complete()
            print('[Player] Playback finished')

    def stop(self):
        """재생 중지"""
        print('[Player] Stopping...')
        self.should_stop = True
        self.is_playing = False
        self.is_paused = False

    def pause(self):
        """일시정지"""
        print('[Player] Paused')
        self.is_paused = True

    def resume(self):
        """재개"""
        print('[Player] Resumed')
        self.is_paused = False

    def _execute_block(self, block: ActionBlock):
        """개별 블록 실행"""
        print(f'[Player] Executing: {block.type} - {block.description}')

        # 콜백: 블록 시작
        if self.on_block_start:
            self.on_block_start(block)

        block.status = ActionStatus.RUNNING
        success = False

        try:
            # 타입별 실행
            if block.type == 'click':
                self._execute_click(block)
            elif block.type == 'dblclick':
                self._execute_double_click(block)
            elif block.type == 'drag':
                self._execute_drag(block)
            elif block.type == 'scroll':
                self._execute_scroll(block)
            elif block.type == 'repeat-click':
                self._execute_repeat_click(block)
            elif block.type == 'type':
                self._execute_type(block)
            elif block.type == 'shortcut':
                self._execute_shortcut(block)
            elif block.type == 'key-repeat':
                self._execute_key_repeat(block)
            elif block.type == 'delay':
                self._execute_delay(block)
            elif block.type == 'condition-image':
                self._execute_condition_image(block)
            elif block.type == 'loop-count':
                self._execute_loop_count(block)
            elif block.type == 'variable-set':
                self._execute_variable_set(block)
            else:
                print(f'[Player] ⚠ Unknown action type: {block.type}')

            block.status = ActionStatus.COMPLETED
            success = True

        except Exception as e:
            print(f'[Player] ✗ Block failed: {e}')
            block.status = ActionStatus.FAILED

            # 재시도 로직 (Phase 8)
            if block.retry_count > 0:
                print(f'[Player] Retrying... ({block.retry_count} attempts left)')
                time.sleep(block.retry_interval / 1000)
                block.retry_count -= 1
                self._execute_block(block)
            else:
                # Fallback 실행
                if block.fallback_children:
                    print('[Player] Executing fallback actions')
                    for child in block.fallback_children:
                        self._execute_block(child)

        finally:
            # 콜백: 블록 종료
            if self.on_block_end:
                self.on_block_end(block, success)

    # --- 액션 실행 메서드 ---

    def _execute_click(self, block: ActionBlock):
        """클릭 실행"""
        p = block.payload
        self.automation.click(
            p.get('x', 0),
            p.get('y', 0),
            button=p.get('button', 'left')
        )

    def _execute_double_click(self, block: ActionBlock):
        """더블클릭 실행"""
        p = block.payload
        self.automation.double_click(
            p.get('x', 0),
            p.get('y', 0),
            button=p.get('button', 'left')
        )

    def _execute_drag(self, block: ActionBlock):
        """드래그 실행"""
        p = block.payload
        self.automation.drag(
            p.get('start_x', 0),
            p.get('start_y', 0),
            p.get('end_x', 0),
            p.get('end_y', 0),
            duration=p.get('duration', 0.5)
        )

    def _execute_scroll(self, block: ActionBlock):
        """스크롤 실행"""
        p = block.payload
        self.automation.scroll(
            p.get('amount', 0),
            x=p.get('x'),
            y=p.get('y')
        )

    def _execute_repeat_click(self, block: ActionBlock):
        """연타 실행"""
        p = block.payload
        self.automation.repeat_click(
            p.get('x', 0),
            p.get('y', 0),
            count=p.get('count', 1),
            interval=p.get('interval', 0.1),
            button=p.get('button', 'left')
        )

    def _execute_type(self, block: ActionBlock):
        """텍스트 입력 실행"""
        p = block.payload
        self.automation.type_text(
            p.get('text', ''),
            interval=p.get('interval', 0.05),
            use_clipboard=p.get('use_clipboard', True)
        )

    def _execute_shortcut(self, block: ActionBlock):
        """단축키 실행"""
        p = block.payload
        keys = p.get('keys', '').split('+')
        self.automation.hotkey(*keys)

    def _execute_key_repeat(self, block: ActionBlock):
        """키 연타 실행"""
        p = block.payload
        self.automation.repeat_key(
            p.get('key', ''),
            count=p.get('count', 1),
            interval=p.get('interval', 0.1)
        )

    def _execute_delay(self, block: ActionBlock):
        """대기 실행"""
        p = block.payload
        duration = p.get('duration', 1000) / 1000  # ms -> s
        self.automation.delay(duration)

    def _execute_condition_image(self, block: ActionBlock):
        """이미지 조건 실행 (Phase 5에서 구현)"""
        print('[Player] ⚠ condition-image: Not implemented yet (Phase 5)')
        # TODO: Phase 5에서 Vision Engine 연동
        pass

    def _execute_loop_count(self, block: ActionBlock):
        """카운트 루프 실행"""
        p = block.payload
        count = p.get('count', 1)
        delay_between = p.get('delay_between', 0) / 1000

        print(f'[Player] Loop: {count} times')

        for i in range(count):
            if self.should_stop:
                break

            print(f'[Player] Loop iteration: {i + 1}/{count}')

            # 자식 블록 실행
            for child in block.children:
                self._execute_block(child)

            # 루프 간격 대기
            if i < count - 1 and delay_between > 0:
                time.sleep(delay_between)

    def _execute_variable_set(self, block: ActionBlock):
        """변수 설정 (Phase 8)"""
        p = block.payload
        var_name = p.get('name', '')
        var_value = p.get('value', '')

        self.variables[var_name] = var_value
        print(f'[Player] Variable set: {var_name} = {var_value}')
