import pytest
from core.workflow_manager import WorkflowManager
from models.action_block import ActionBlock

def test_workflow_crud():
    """워크플로우 생성, 수정, 삭제 테스트"""
    wm = WorkflowManager()
    
    # 1. 추가
    block1 = ActionBlock(type="click", payload={"x": 100, "y": 100})
    wm.add_block(block1)
    assert len(wm.blocks) == 1
    
    # 2. 수정
    wm.update_block(block1.id, {"description": "Modified Click"})
    assert wm.blocks[0].description == "Modified Click"
    
    # 3. 삭제
    wm.delete_block(block1.id)
    assert len(wm.blocks) == 0

def test_workflow_reorder():
    """블록 순서 변경 테스트"""
    wm = WorkflowManager()
    b1 = ActionBlock(type="click", description="First")
    b2 = ActionBlock(type="type", description="Second")
    
    wm.add_block(b1)
    wm.add_block(b2)
    
    # 순서 바꾸기 (b2를 0번으로)
    wm.move_block(b2.id, 0)
    assert wm.blocks[0].description == "Second"
    assert wm.blocks[1].description == "First"
