import pytest
from app.core.celery_app import celery_app


def test_celery_app_exists():
    """Test that Celery app is properly configured"""
    assert celery_app is not None
    assert celery_app.main == "speech_practice"


def test_celery_task_routes():
    """Test that task routes are configured correctly"""
    routes = celery_app.conf.task_routes
    assert routes is not None
    assert 'app.tasks.stt.*' in routes
    assert 'app.tasks.prosody.*' in routes
    assert 'app.tasks.llm.*' in routes
    assert routes['app.tasks.stt.*']['queue'] == 'stt'
    assert routes['app.tasks.prosody.*']['queue'] == 'prosody'
    assert routes['app.tasks.llm.*']['queue'] == 'llm'


def test_celery_serializer_config():
    """Test that serializer configuration is correct"""
    assert celery_app.conf.task_serializer == 'json'
    assert celery_app.conf.result_serializer == 'json'
    assert 'json' in celery_app.conf.accept_content
