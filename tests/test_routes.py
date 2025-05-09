from fastapi.testclient import TestClient
from api.depends import get_db_session
from api.main import api
from unittest.mock import MagicMock, patch
import pytest


mock_session = MagicMock()
function_mock = MagicMock()

def override_get_db_session():
    try:
        yield mock_session
    finally:
        pass

api.dependency_overrides[get_db_session] = override_get_db_session



@pytest.fixture
def mock_db_session():
    return mock_session


client = TestClient(api)


######User register############
@patch('api.cases.auth.AuthUseCases.user_register', function_mock)
def test_user_register_OK():
    response = client.post("/auth/register", json={'email': 'test@test.test', 'password': '123'})

    assert function_mock.assert_called_once
    assert response.status_code == 201
    
    function_mock.reset_mock(return_value=True)

