from api.cases.auth import AuthUseCases
from api.schemas import User
from unittest.mock import MagicMock, patch
import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timezone

mock_session = MagicMock()
crypt_context = CryptContext(schemes=['sha256_crypt'])


def test_user_register_OK():
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "123")
    case.user_register(user)

    assert mock_session.add.call_count == 2
    assert mock_session.commit.call_count == 1


def test_user_register_existing_email():
    mock_session.commit.side_effect = IntegrityError('', '', '')
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test"  , password =  "123")
    with pytest.raises(HTTPException):
        case.user_register(user)


@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_login_OK():
    mock_user = User(email = "test@test.test" , password = crypt_context.hash("123"))
    mock_session.query().filter_by().first.return_value = mock_user
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "123")
    login = case.user_login(user)

    assert 'access_token' in login
    assert 'expire_date' in login

@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_login_bad_password():
    mock_user = User(email = "test@test.test" , password = crypt_context.hash("1234"))
    mock_session.query().filter_by().first.return_value = mock_user
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "123")
    with pytest.raises(HTTPException):
        case.user_login(user)

@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_login_bad_password():
    mock_session.query().filter_by().first.return_value = None
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "123")
    with pytest.raises(HTTPException):
        case.user_login(user)

@patch('api.cases.auth.SECRET_KEY', '3')
def test_verify_token_OK():
    payload = {
            'sub' : "test@test.test",
            'exp' : datetime.now(timezone.utc)
        }
    
    mock_user = User(email = "test@test.test" , password = crypt_context.hash("123"))
    mock_session.query().filter_by().first.return_value = mock_user

    access_token = jwt.encode(payload, '3', algorithm='HS256')
    case = AuthUseCases(mock_session)
    user = case.verify_token(access_token)

    assert user is not None

@patch('api.cases.auth.SECRET_KEY', '3')
def test_verify_token_invalid_JWT():
    case = AuthUseCases(mock_session)
    with pytest.raises(HTTPException):
        case.verify_token('test')

@patch('api.cases.auth.SECRET_KEY', '3')
def test_verify_token_no_user():
    payload = {
            'sub' : "test@test.test",
            'exp' : datetime.now(timezone.utc)
        }
    
    mock_session.query().filter_by().first.return_value = None

    access_token = jwt.encode(payload, '3', algorithm='HS256')
    case = AuthUseCases(mock_session)
    with pytest.raises(HTTPException):
        case.verify_token(access_token)

