"""
ActionBlock - 자동화 액션 블록 데이터 모델
TypeScript 원본: main/types/index.ts
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class ActionBlock:
    """
    단일 자동화 액션 블록

    지원 타입:
    - 마우스: click, dblclick, drag, scroll, repeat-click
    - 키보드: type, shortcut, key-repeat
    - 흐름: delay, condition-image
    - 변수: variable-set, variable-get, variable-calc, variable-ocr
    - 루프: loop-count, loop-while-image, loop-foreach
    - 고급: wait-until-image, wait-until-color, execute-macro, ocr-extract, ocr-condition
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ''  # 'click', 'drag', 'type', 'delay', 'condition-image', etc.
    payload: Dict[str, Any] = field(default_factory=dict)
    description: str = ''
    children: List['ActionBlock'] = field(default_factory=list)
    elseChildren: List['ActionBlock'] = field(default_factory=list)
    status: Optional[str] = None  # 'running', 'completed', 'skipped', 'failed'

    # Phase 8 고급 기능 필드
    retry_count: int = 0  # 재시도 횟수
    retry_interval: int = 1000  # 재시도 간격 (ms)
    fallback_children: List['ActionBlock'] = field(default_factory=list)  # 재시도 실패 시 실행

    def to_dict(self) -> dict:
        """JSON 직렬화"""
        return {
            'id': self.id,
            'type': self.type,
            'payload': self.payload,
            'description': self.description,
            'children': [child.to_dict() for child in self.children],
            'elseChildren': [child.to_dict() for child in self.elseChildren],
            'status': self.status,
            'retry_count': self.retry_count,
            'retry_interval': self.retry_interval,
            'fallback_children': [child.to_dict() for child in self.fallback_children]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ActionBlock':
        """JSON 역직렬화"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            type=data.get('type', ''),
            payload=data.get('payload', {}),
            description=data.get('description', ''),
            children=[cls.from_dict(child) for child in data.get('children', [])],
            elseChildren=[cls.from_dict(child) for child in data.get('elseChildren', [])],
            status=data.get('status'),
            retry_count=data.get('retry_count', 0),
            retry_interval=data.get('retry_interval', 1000),
            fallback_children=[cls.from_dict(child) for child in data.get('fallback_children', [])]
        )

    def clone(self) -> 'ActionBlock':
        """깊은 복사"""
        return ActionBlock.from_dict(self.to_dict())


# 액션 타입 상수
class ActionType:
    # 마우스
    CLICK = 'click'
    DOUBLE_CLICK = 'dblclick'
    DRAG = 'drag'
    SCROLL = 'scroll'
    REPEAT_CLICK = 'repeat-click'

    # 키보드
    TYPE = 'type'
    SHORTCUT = 'shortcut'
    KEY_REPEAT = 'key-repeat'

    # 흐름
    DELAY = 'delay'
    CONDITION_IMAGE = 'condition-image'

    # 변수
    VARIABLE_SET = 'variable-set'
    VARIABLE_GET = 'variable-get'
    VARIABLE_CALC = 'variable-calc'
    VARIABLE_OCR = 'variable-ocr'

    # 루프
    LOOP_COUNT = 'loop-count'
    LOOP_WHILE_IMAGE = 'loop-while-image'
    LOOP_FOREACH = 'loop-foreach'

    # 고급
    WAIT_UNTIL_IMAGE = 'wait-until-image'
    WAIT_UNTIL_COLOR = 'wait-until-color'
    EXECUTE_MACRO = 'execute-macro'
    OCR_EXTRACT = 'ocr-extract'
    OCR_CONDITION = 'ocr-condition'
    EXCEL_READ = 'excel-read'
    EXCEL_WRITE = 'excel-write'
    PDF_EXTRACT = 'pdf-extract'


# 액션 상태 상수
class ActionStatus:
    RUNNING = 'running'
    COMPLETED = 'completed'
    SKIPPED = 'skipped'
    FAILED = 'failed'
