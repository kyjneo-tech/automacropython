from typing import List, Dict, Callable, Optional, Any
from src.domain.actions import ActionNode, ActionType

class AppState:
    def __init__(self):
        self.nodes: Dict[str, ActionNode] = {}
        self.selected_node_id: Optional[str] = None
        
        # Initialize with a START node - REMOVED per user request
        # start_node = ActionNode(type=ActionType.START, label="Start", x=100, y=100)
        # self.nodes[start_node.id] = start_node

class Store:
    def __init__(self):
        self.state = AppState()
        self._observers: List[Callable] = []

    def subscribe(self, callback: Callable):
        self._observers.append(callback)
        
    def notify(self, event_type: str = "ALL", payload: Any = None):
        for callback in self._observers:
            callback(event_type, payload)

    # --- Actions (Reducers equivalent) ---

    def add_node(self, node: ActionNode):
        self.state.nodes[node.id] = node
        self.notify("STRUCTURE")

    def remove_node(self, node_id: str):
        if node_id in self.state.nodes:
            del self.state.nodes[node_id]
            if self.state.selected_node_id == node_id:
                self.state.selected_node_id = None
            self.notify("STRUCTURE")

    def update_node_position(self, node_id: str, x: float, y: float):
        if node_id in self.state.nodes:
            self.state.nodes[node_id].x = x
            self.state.nodes[node_id].y = y
            self.notify("POSITION", node_id)
            
    def update_node_params(self, node_id: str, params: Dict):
        if node_id in self.state.nodes:
            self.state.nodes[node_id].params.update(params)
            self.notify("PARAMS", node_id)

    def select_node(self, node_id: Optional[str]):
        if self.state.selected_node_id == node_id:
            return
            
        self.state.selected_node_id = node_id
        self.notify("SELECTION", node_id)

    def connect_nodes(self, source_id: str, target_id: str):
        if source_id in self.state.nodes:
            self.state.nodes[source_id].next_node_id = target_id
            self.notify("STRUCTURE")
            
    def get_node(self, node_id: str) -> Optional[ActionNode]:
        return self.state.nodes.get(node_id)
        
    def get_all_nodes(self) -> List[ActionNode]:
        return list(self.state.nodes.values())
