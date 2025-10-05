"""
Tests for Context Cache
"""

import pytest
import json
from pathlib import Path
from mcp_server.utils import ContextCache


@pytest.fixture
def json_cache(tmp_path):
    """JSON cache fixture"""
    cache_file = tmp_path / "test_cache.json"
    cache = ContextCache(cache_type="json", cache_path=str(cache_file))
    yield cache
    cache.close()


def test_json_cache_init(json_cache):
    """Test JSON cache initialization"""
    assert json_cache.cache_type == "json"
    assert json_cache.cache_path.exists()


def test_save_conversation(json_cache):
    """Test saving conversation"""
    json_cache.save_conversation(
        user_input="Create a box",
        llm_response="Creating box...",
        provider="openai",
        model="gpt-4o-mini"
    )

    conversations = json_cache.get_recent_conversations(limit=1)
    assert len(conversations) == 1
    assert conversations[0]["user_input"] == "Create a box"
    assert conversations[0]["provider"] == "openai"


def test_save_design_state(json_cache):
    """Test saving design state"""
    context = {
        "active_component": "RootComponent",
        "units": "mm",
        "design_state": "empty"
    }

    json_cache.save_design_state(context)
    # Just verify no errors - retrieval test would need more complex logic


def test_save_action(json_cache):
    """Test saving action"""
    json_cache.save_action(
        action_type="create_box",
        action_data={"width": 20, "height": 20},
        success=True
    )

    actions = json_cache.get_recent_actions(limit=1)
    assert len(actions) == 1
    assert actions[0]["action_type"] == "create_box"
    assert actions[0]["success"] is True


def test_clear_cache(json_cache):
    """Test clearing cache"""
    json_cache.save_conversation(
        user_input="Test",
        llm_response="Response",
        provider="test",
        model="test"
    )

    json_cache.clear_cache()

    conversations = json_cache.get_recent_conversations()
    assert len(conversations) == 0
