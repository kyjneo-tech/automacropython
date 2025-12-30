import pytest
from src.state.store import Store
from src.domain.actions import ActionNode, ActionType
from src.domain.runner import WorkflowRunner
from unittest.mock import MagicMock

@pytest.fixture
def setup_runner():
    store = Store()
    driver = MagicMock()
    runner = WorkflowRunner(store, driver)
    return runner, store, driver

def test_variable_set_and_interpolation(setup_runner):
    runner, store, driver = setup_runner
    
    # 1. Set variable 'count' to 10
    node_set = ActionNode(type=ActionType.VARIABLE_SET, params={"variable_name": "count", "value": "10"})
    runner._execute_node(node_set)
    assert runner.variables["count"] == 10
    
    # 2. Use variable in text: "Value is 10"
    node_text = ActionNode(type=ActionType.KEYBOARD_INPUT, params={"mode": "text", "text": "Value is {count}"})
    runner._execute_node(node_text)
    
    driver.type_text.assert_called_with("Value is 10", 0.05)

def test_if_condition_branching(setup_runner):
    runner, store, driver = setup_runner
    
    # Set count = 5
    runner.variables["count"] = 5
    
    # Condition: count > 3 (True)
    node_if = ActionNode(type=ActionType.IF_CONDITION, params={"condition": "count > 3"})
    result = runner._execute_node(node_if)
    assert result is True
    
    # Condition: count < 0 (False)
    node_if.params["condition"] = "count < 0"
    result = runner._execute_node(node_if)
    assert result is False

def test_workflow_branching_execution(setup_runner):
    runner, store, driver = setup_runner
    
    # Create 3 nodes: IF -> NodeA (True), NodeB (False)
    node_if = ActionNode(id="if_node", type=ActionType.IF_CONDITION, params={"condition": "val == 1"})
    node_true = ActionNode(id="true_path", label="TrueNode")
    node_false = ActionNode(id="false_path", label="FalseNode")
    
    node_if.true_node_id = "true_path"
    node_if.false_node_id = "false_path"
    
    store.add_node(node_if)
    store.add_node(node_true)
    store.add_node(node_false)
    
    # Test True path
    runner.variables["val"] = 1
    # Mocking _run_loop's while to only run one step or testing via internal logic
    # Here we just verify which ID is chosen in _run_loop logic
    
    # Execute node_if and see where it goes
    result = runner._execute_node(node_if)
    next_id = node_if.true_node_id if result else node_if.false_node_id
    assert next_id == "true_path"
    
    # Test False path
    runner.variables["val"] = 0
    result = runner._execute_node(node_if)
    next_id = node_if.true_node_id if result else node_if.false_node_id
    assert next_id == "false_path"
