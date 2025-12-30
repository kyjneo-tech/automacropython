from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid

class ActionType(Enum):
    CLICK = "CLICK"
    KEYBOARD_INPUT = "KEYBOARD_INPUT"
    WAIT = "WAIT"
    IMAGE_MATCH = "IMAGE_MATCH"
    MOUSE_MOVE = "MOUSE_MOVE"
    SCROLL = "SCROLL"
    DRAG = "DRAG"
    
    # New Advanced Actions
    IF_CONDITION = "IF_CONDITION"
    LOOP = "LOOP"
    VARIABLE_SET = "VARIABLE_SET"
    OCR_READ = "OCR_READ"

@dataclass
class ActionNode:
    """
    Represents a Node in the automation graph.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ActionType = ActionType.CLICK
    label: str = "Action"
    
    # Visual Position in Graph
    x: float = 0.0
    y: float = 0.0
    
    # Parameters (Dynamic based on type)
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Graph Connections
    next_node_id: Optional[str] = None # Default flow
    true_node_id: Optional[str] = None # For IF (Success/True)
    false_node_id: Optional[str] = None # For IF (Failure/False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "params": self.params,
            "next_node_id": self.next_node_id,
            "true_node_id": self.true_node_id,
            "false_node_id": self.false_node_id
        }

    @staticmethod
    def from_dict(data):
        node = ActionNode(
            id=data.get("id"),
            type=ActionType(data.get("type")),
            label=data.get("label", "Action"),
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            params=data.get("params", {}),
            next_node_id=data.get("next_node_id"),
            true_node_id=data.get("true_node_id"),
            false_node_id=data.get("false_node_id")
        )
        return node
