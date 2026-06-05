#!/usr/bin/env python3
"""
Unit tests for exprule core
"""

import pytest
from exprule.core.experience import Experience, Task, Step, Action, generate_id
from exprule.core.context import Context
from exprule.core.feedback import Feedback, FeedbackType
from exprule.storage.memory import MemoryStorage
from exprule.engine.query_engine import QueryEngine
from exprule.engine.update_engine import UpdateEngine
from exprule.agents.base_agent import BaseAgentAdapter


def test_experience_creation():
    """Test that we can create a basic experience structure."""
    action = Action(
        action_name="Test Action",
        description="A test action"
    )
    step = Step(
        step_name="Test Step",
        description="A test step",
        order=0,
        actions=[action]
    )
    task = Task(
        task_name="Test Task",
        description="A test task",
        goal="Complete the test",
        steps=[step],
        tags=["test", "example"]
    )
    exp = Experience(task=task)
    
    assert exp.experience_id is not None
    assert len(exp.task.steps) == 1
    assert len(exp.task.steps[0].actions) == 1


def test_context_similarity():
    """Test context similarity calculation."""
    ctx1 = Context(
        context_id="ctx1",
        tags=["python", "coding"],
        user_id="user1"
    )
    ctx2 = Context(
        context_id="ctx2",
        tags=["python", "testing"],
        user_id="user1"
    )
    similarity = ctx1.similarity_score(ctx2)
    assert similarity > 0


def test_feedback_conversion():
    """Test feedback to learning signal conversion."""
    fb_success = Feedback(
        feedback_id="fb1", experience_id="exp1", feedback_type=FeedbackType.SUCCESS, score=0.9)
    assert fb_success.get_learning_signal() == 0.9
    
    fb_failure = Feedback(
        feedback_id="fb2", experience_id="exp1", feedback_type=FeedbackType.FAILURE, score=0.1)
    assert fb_failure.get_learning_signal() == 0.1


def test_memory_storage():
    """Test memory storage operations."""
    storage = MemoryStorage()
    
    task = Task(task_name="Test", description="Test", goal="Test")
    exp = Experience(task=task)
    
    storage.save_experience(exp)
    assert storage.get_experience_count() == 1
    
    retrieved = storage.get_experience(exp.experience_id)
    assert retrieved is not None
    assert retrieved.task.task_name == "Test"
    
    deleted = storage.delete_experience(exp.experience_id)
    assert deleted is True
    assert storage.get_experience_count() == 0


def test_query_engine():
    """Test query engine functionality."""
    storage = MemoryStorage()
    query_engine = QueryEngine(storage)
    
    task1 = Task(
        task_name="Python Coding",
        description="Write Python code",
        goal="Write Python",
        tags=["python", "coding"],
        weight=0.8
    )
    exp1 = Experience(task=task1)
    
    task2 = Task(
        task_name="JavaScript Coding",
        description="Write JavaScript code",
        goal="Write JS",
        tags=["javascript", "coding"],
        weight=0.6
    )
    exp2 = Experience(task=task2)
    
    storage.save_experience(exp1)
    storage.save_experience(exp2)
    
    results = query_engine.query("python")
    assert len(results) > 0
    assert results[0][0].task.task_name == "Python Coding"


def test_update_engine():
    """Test update engine weight updates."""
    storage = MemoryStorage()
    update_engine = UpdateEngine(storage, learning_rate=0.5)
    
    task = Task(task_name="Test", description="Test", goal="Test", weight=0.5)
    exp = Experience(task=task)
    storage.save_experience(exp)
    
    updated = update_engine.record_success(exp.experience_id)
    assert updated is not None
    assert updated.task.weight > 0.5
    
    updated = update_engine.record_failure(exp.experience_id)
    assert updated.task.weight < 0.8


def test_agent_adapter():
    """Test base agent adapter."""
    agent = BaseAgentAdapter(agent_id="test_agent")
    
    exp = agent.create_simple_experience(
        task_name="Test Task",
        description="Test",
        goal="Test"
    )
    agent.record_experience(exp)
    
    found = agent.query_experience("test")
    assert found is not None
    
    updated = agent.update_feedback(exp.experience_id, success=True)
    assert updated is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
