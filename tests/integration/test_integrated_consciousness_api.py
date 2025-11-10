
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from serve.api.integrated_consciousness_api import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_consciousness_engine():
    mock_engine = MagicMock()
    mock_engine.get_current_state = AsyncMock(return_value=MagicMock(name='State', awareness=0.9, thoughts=[], emotion='neutral', context_size=10, timestamp=MagicMock(isoformat=lambda: '2023-10-27T10:00:00')))
    mock_engine.process_thought = AsyncMock(return_value=MagicMock(id='thought1', content='processed', associations=[], emotions={}, memories=[]))
    mock_engine.enter_dream_state = AsyncMock(return_value=MagicMock(id='dream1'))
    mock_engine.get_dream_outputs = AsyncMock(return_value=[MagicMock(complete=True, insight='dream insight')])
    mock_engine.store_memory = AsyncMock(return_value='memory1')
    mock_engine.recall = AsyncMock(return_value=[MagicMock(to_dict=lambda: {'id': 'mem1'})])
    mock_engine.analyze_self_awareness = AsyncMock(return_value=MagicMock(score=0.8, depth=5, insights=[]))

    with pytest.MonkeyPatch.context() as m:
        m.setattr('serve.api.integrated_consciousness_api.consciousness_engine', mock_engine)
        yield mock_engine

def test_get_consciousness_state():
    response = client.get('/consciousness/state')
    assert response.status_code == 200
    json_response = response.json()
    assert json_response['awareness_level'] == 0.9

def test_process_thought():
    response = client.post('/consciousness/think', json={'content': 'test'})
    assert response.status_code == 200
    assert response.json()['thought_id'] == 'thought1'

def test_enter_dream_state():
    response = client.post('/consciousness/dream', json={'seeds': ['test'], 'duration': 60, 'creativity_level': 0.7})
    assert response.status_code == 200
    assert response.json()['session_id'] == 'dream1'

def test_get_dream_outputs():
    response = client.get('/consciousness/dream/dream1')
    assert response.status_code == 200
    assert response.json()['state'] == 'completed'

def test_store_consciousness_memory():
    response = client.post('/consciousness/remember', json={'experience': 'test', 'context': {}, 'importance': 0.8})
    assert response.status_code == 200
    assert response.json()['memory_id'] == 'memory1'

def test_recall_memory():
    response = client.post('/consciousness/recall', json={'query': 'test'})
    assert response.status_code == 200
    assert len(response.json()['memories']) == 1

def test_get_self_awareness():
    response = client.get('/consciousness/self-awareness')
    assert response.status_code == 200
    assert response.json()['awareness_score'] == 0.8
