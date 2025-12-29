"""
Recorder - 마우스/키보드 녹화
pynput 기반 전역 후킹
"""

import time
from typing import List, Callable, Optional, Tuple
from pynput import mouse, keyboard

try:
    from models import ActionBlock, ActionType
except ImportError:
    from ..models import ActionBlock, ActionType


class Recorder:
    """액션 녹화기"""

    def __init__(self):
        self.is_recording = False
        self.recorded_blocks: List[ActionBlock] = []

        # 리스너
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None

        # 마우스 상태 추적
        self.mouse_down_pos: Optional[Tuple[int, int]] = None
        self.mouse_down_time: float = 0
        self.last_click_time: float = 0
        self.last_click_pos: Optional[Tuple[int, int]] = None

        # 키보드 상태 추적
        self.pressed_keys: set = set()
        self.typed_text: str = ''

        # 콜백
        self.on_action_recorded: Optional[Callable[[ActionBlock], None]] = None

        # 임계값
        self.DOUBLE_CLICK_THRESHOLD = 0.5  # 초
        self.DRAG_DISTANCE_THRESHOLD = 5  # 픽셀
        self.TEXT_FLUSH_DELAY = 1.0  # 초

        print('[Recorder] Initialized')

    def start(self):
        """녹화 시작"""
        if self.is_recording:
            print('[Recorder] Already recording')
            return

        print('[Recorder] Starting recording...')
        self.is_recording = True
        self.recorded_blocks.clear()

        # 마우스 리스너 시작
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self.mouse_listener.start()

        # 키보드 리스너 시작
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()

        print('[Recorder] ⏺️ Recording...')

    def stop(self) -> List[ActionBlock]:
        """
        녹화 중지

        Returns:
            녹화된 블록 리스트
        """
        if not self.is_recording:
            print('[Recorder] Not recording')
            return []

        print('[Recorder] Stopping recording...')
        self.is_recording = False

        # 리스너 중지
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

        # 남은 텍스트 플러시
        self._flush_typed_text()

        print(f'[Recorder] ⏹️ Stopped. Recorded {len(self.recorded_blocks)} actions')
        return self.recorded_blocks.copy()

    def clear(self):
        """녹화된 블록 초기화"""
        self.recorded_blocks.clear()
        print('[Recorder] Cleared recorded actions')

    # --- 마우스 이벤트 ---

    def _on_mouse_move(self, x: int, y: int):
        """마우스 이동 (드래그 감지용)"""
        if not self.is_recording:
            return

        # 드래그 감지: 마우스를 누른 상태에서 이동
        if self.mouse_down_pos:
            dx = abs(x - self.mouse_down_pos[0])
            dy = abs(y - self.mouse_down_pos[1])

            # 임계값 이상 이동하면 드래그로 간주
            if dx > self.DRAG_DISTANCE_THRESHOLD or dy > self.DRAG_DISTANCE_THRESHOLD:
                # 이미 드래그 블록이 있으면 업데이트, 없으면 새로 생성
                if not self.recorded_blocks or self.recorded_blocks[-1].type != ActionType.DRAG:
                    pass  # 드래그 블록은 release에서 생성

    def _on_mouse_click(self, x: int, y: int, button, pressed: bool):
        """마우스 클릭"""
        if not self.is_recording:
            return

        current_time = time.time()

        if pressed:
            # 마우스 다운
            self.mouse_down_pos = (x, y)
            self.mouse_down_time = current_time

        else:
            # 마우스 업
            if not self.mouse_down_pos:
                return

            start_x, start_y = self.mouse_down_pos
            dx = abs(x - start_x)
            dy = abs(y - start_y)

            button_str = button.name  # 'left', 'right', 'middle'

            # 드래그 감지
            if dx > self.DRAG_DISTANCE_THRESHOLD or dy > self.DRAG_DISTANCE_THRESHOLD:
                # 드래그 블록 생성
                block = ActionBlock(
                    type=ActionType.DRAG,
                    payload={
                        'start_x': start_x,
                        'start_y': start_y,
                        'end_x': x,
                        'end_y': y,
                        'duration': 0.5
                    },
                    description=f'드래그: ({start_x}, {start_y}) → ({x}, {y})'
                )
                self._add_block(block)

            else:
                # 더블클릭 감지
                is_double_click = False
                if self.last_click_pos and self.last_click_time:
                    time_diff = current_time - self.last_click_time
                    pos_diff = abs(x - self.last_click_pos[0]) + abs(y - self.last_click_pos[1])

                    if time_diff < self.DOUBLE_CLICK_THRESHOLD and pos_diff < 10:
                        is_double_click = True

                if is_double_click:
                    # 이전 클릭 블록 제거하고 더블클릭으로 교체
                    if self.recorded_blocks and self.recorded_blocks[-1].type == ActionType.CLICK:
                        self.recorded_blocks.pop()

                    block = ActionBlock(
                        type=ActionType.DOUBLE_CLICK,
                        payload={
                            'x': x,
                            'y': y,
                            'button': button_str
                        },
                        description=f'더블클릭: ({x}, {y})'
                    )
                    self._add_block(block)

                else:
                    # 일반 클릭
                    block = ActionBlock(
                        type=ActionType.CLICK,
                        payload={
                            'x': x,
                            'y': y,
                            'button': button_str
                        },
                        description=f'클릭: ({x}, {y})'
                    )
                    self._add_block(block)

                # 마지막 클릭 기록
                self.last_click_time = current_time
                self.last_click_pos = (x, y)

            # 마우스 다운 상태 초기화
            self.mouse_down_pos = None

    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int):
        """마우스 스크롤"""
        if not self.is_recording:
            return

        # dy: 양수(위로), 음수(아래로)
        block = ActionBlock(
            type=ActionType.SCROLL,
            payload={
                'amount': int(dy),
                'x': x,
                'y': y
            },
            description=f'스크롤: {"위" if dy > 0 else "아래"} ({abs(dy)})'
        )
        self._add_block(block)

    # --- 키보드 이벤트 ---

    def _on_key_press(self, key):
        """키 눌림"""
        if not self.is_recording:
            return

        try:
            # 특수 키 처리
            if hasattr(key, 'name'):
                key_name = key.name
            else:
                key_name = key.char if hasattr(key, 'char') else str(key)

            # 이미 눌린 키면 무시 (키 리피트 방지)
            if key_name in self.pressed_keys:
                return

            self.pressed_keys.add(key_name)

            # 단축키 감지 (Ctrl, Shift, Alt 등)
            modifier_keys = {'ctrl_l', 'ctrl_r', 'shift', 'shift_l', 'shift_r', 'alt_l', 'alt_r', 'cmd'}

            if any(mod in self.pressed_keys for mod in modifier_keys):
                # 단축키로 간주
                self._flush_typed_text()
                self._record_shortcut()
            else:
                # 일반 텍스트 입력
                if hasattr(key, 'char') and key.char:
                    self.typed_text += key.char

        except Exception as e:
            print(f'[Recorder] Key press error: {e}')

    def _on_key_release(self, key):
        """키 뗌"""
        if not self.is_recording:
            return

        try:
            if hasattr(key, 'name'):
                key_name = key.name
            else:
                key_name = key.char if hasattr(key, 'char') else str(key)

            if key_name in self.pressed_keys:
                self.pressed_keys.remove(key_name)

            # 모든 키를 뗐을 때 텍스트 플러시
            if not self.pressed_keys and self.typed_text:
                time.sleep(self.TEXT_FLUSH_DELAY)
                if not self.pressed_keys:  # 다시 확인
                    self._flush_typed_text()

        except Exception as e:
            print(f'[Recorder] Key release error: {e}')

    def _record_shortcut(self):
        """단축키 녹화"""
        # 현재 눌린 키들을 조합하여 단축키 생성
        keys = sorted(self.pressed_keys)

        # 키 이름 정규화
        normalized_keys = []
        for k in keys:
            if k in ['ctrl_l', 'ctrl_r']:
                normalized_keys.append('ctrl')
            elif k in ['shift', 'shift_l', 'shift_r']:
                normalized_keys.append('shift')
            elif k in ['alt_l', 'alt_r']:
                normalized_keys.append('alt')
            elif k == 'cmd':
                normalized_keys.append('cmd')
            else:
                normalized_keys.append(k)

        # 중복 제거
        normalized_keys = list(dict.fromkeys(normalized_keys))

        if len(normalized_keys) >= 2:
            keys_str = '+'.join(normalized_keys)

            block = ActionBlock(
                type=ActionType.SHORTCUT,
                payload={'keys': keys_str},
                description=f'단축키: {keys_str}'
            )
            self._add_block(block)

    def _flush_typed_text(self):
        """입력된 텍스트를 블록으로 변환"""
        if self.typed_text:
            block = ActionBlock(
                type=ActionType.TYPE,
                payload={
                    'text': self.typed_text,
                    'use_clipboard': True
                },
                description=f'텍스트 입력: "{self.typed_text[:30]}..."'
            )
            self._add_block(block)
            self.typed_text = ''

    def _add_block(self, block: ActionBlock):
        """블록 추가"""
        self.recorded_blocks.append(block)
        print(f'[Recorder] + Recorded: {block.type} - {block.description}')

        if self.on_action_recorded:
            self.on_action_recorded(block)
