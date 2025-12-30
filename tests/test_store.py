import pytest
from src.state.store import Store
from src.domain.actions import ActionNode, ActionType

def test_initial_state():
    store = Store()
    nodes = store.get_all_nodes()
    assert len(nodes) == 0
    assert store.state.selected_node_id is None

def test_add_remove_node():
    store = Store()
    new_node = ActionNode(type=ActionType.CLICK, label="Click 1")
    
    # Test Add
    store.add_node(new_node)
    assert len(store.get_all_nodes()) == 1
    assert store.get_node(new_node.id) is not None
    
    # Test Remove
    store.remove_node(new_node.id)
    assert len(store.get_all_nodes()) == 0
    assert store.get_node(new_node.id) is None

def test_selection():
    store = Store()
    node = ActionNode(type=ActionType.CLICK)
    store.add_node(node)
    
    store.select_node(node.id)
    assert store.state.selected_node_id == node.id
    
    store.select_node(None)
    assert store.state.selected_node_id is None

def test_observer_notification():
    store = Store()
    notify_count = 0
    
    def on_change(*args):
        nonlocal notify_count
        notify_count += 1
        
    store.subscribe(on_change)
    
    node = ActionNode()
    store.add_node(node)
    
    assert notify_count == 1
    
    store.select_node(node.id)
    assert notify_count == 2
