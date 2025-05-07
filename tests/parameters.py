from unittest.mock import MagicMock
import pytest
from api.main import api
from api.depends import get_db_session, token_verifier

mock_session = MagicMock()

def override_get_db_session():
    try:
        yield mock_session
    finally:
        pass

api.dependency_overrides[get_db_session] = override_get_db_session

@pytest.fixture
def mock_db_session():
    return mock_session

def override_token_verifier():
    pass


