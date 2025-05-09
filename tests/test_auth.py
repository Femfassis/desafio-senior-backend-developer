from api.cases.auth import AuthUseCases
from api.schemas import User
from unittest.mock import MagicMock, patch
import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timezone, timedelta


crypt_context = CryptContext(schemes=['sha256_crypt'])
mock_session = MagicMock()
mock_user = MagicMock()
mock_user.email = "test@test.test"
mock_user.password = crypt_context.hash("123")
mock_user.special_token = f'123456|{(datetime.now(timezone.utc) + timedelta(hours=24)).strftime("%d/%m/%Y, %H:%M")}'


######User Register#############
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

    with pytest.raises(HTTPException, match='400: Email already in use'):
        case.user_register(user)
    mock_session.reset_mock(side_effect=True) #Reseta o side_effetct



######User Login#############
@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_login_OK():

    mock_session.query().filter_by().first.return_value = mock_user
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "123")
    login = case.user_login(user)

    assert 'access_token' in login
    assert 'expire_date' in login

@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_login_bad_password():

    mock_session.query().filter_by().first.return_value = mock_user
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "1234")

    with pytest.raises(HTTPException, match='401: Invalid email or password'):
        case.user_login(user)

@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_login_bad_user():

    mock_session.query().filter_by().first.return_value = None
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "123")

    with pytest.raises(HTTPException, match='401: Invalid email or password'):
        case.user_login(user)




######Verify Token#############
@patch('api.cases.auth.SECRET_KEY', '3')
def test_verify_token_OK():

    payload = {
            'sub' : "test@test.test",
            'exp' : datetime.now(timezone.utc)+timedelta(minutes=30)
        }
    
    mock_session.query().filter_by().first.return_value = mock_user

    access_token = jwt.encode(payload, '3', algorithm='HS256')
    case = AuthUseCases(mock_session)
    user = case.verify_token(access_token)

    assert user is not None

@patch('api.cases.auth.SECRET_KEY', '3')
def test_verify_token_invalid_JWT():
    
    case = AuthUseCases(mock_session)

    with pytest.raises(HTTPException, match='401: Invalid access token'):
        case.verify_token('test')

@patch('api.cases.auth.SECRET_KEY', '3')
def test_verify_token_no_user():

    payload = {
            'sub' : "test@test.test",
            'exp' : datetime.now(timezone.utc)+timedelta(minutes=30)
        }
    
    mock_session.query().filter_by().first.return_value = None

    access_token = jwt.encode(payload, '3', algorithm='HS256')
    case = AuthUseCases(mock_session)
    with pytest.raises(HTTPException, match='401: Invalid access token'):
        case.verify_token(access_token)

@patch('api.cases.auth.SECRET_KEY', '3')
def test_verify_token_expired():

    payload = {
            'sub' : "test@test.test",
            'exp' : datetime.now(timezone.utc)-timedelta(minutes=30)
        }
    

    access_token = jwt.encode(payload, '3', algorithm='HS256')
    case = AuthUseCases(mock_session)
    
    with pytest.raises(HTTPException, match='401: Invalid access token'):
        case.verify_token(access_token)






######User Login Part One#############

def test_user_login_part_one_OK():
    mock_session.query().filter_by().first.return_value = mock_user
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "123")
    login = case.user_login_part_one(user)

    assert 'special_token' in login
    assert 'email' in login
    assert mock_session.commit.assert_called_once



def test_user_login_part_one_bad_password():
    mock_session.query().filter_by().first.return_value = mock_user
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "1234")
    with pytest.raises(HTTPException, match='401: Invalid email or password'):
        case.user_login_part_one(user)


def test_user_login_part_one_bad_user():
    mock_session.query().filter_by().first.return_value = None
    case = AuthUseCases(mock_session)
    user = User(email = "test@test.test" , password =  "123")
    with pytest.raises(HTTPException, match='401: Invalid email or password'):
        case.user_login_part_one(user)

######User Login Part Two#############

@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_part_two_login_OK():
    mock_session.query().filter_by().first.return_value = mock_user
    case = AuthUseCases(mock_session)
    login = case.user_login_part_two(email=mock_user.email, special_token=mock_user.special_token.split('|')[0])

    assert 'access_token' in login
    assert 'expire_date' in login

@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_login_part_two__bad_special_token_number():

    mock_user.special_token = f'123456|{(datetime.now(timezone.utc) + timedelta(hours=24)).strftime("%d/%m/%Y, %H:%M")}'
    mock_session.query().filter_by().first.return_value = mock_user
    case = AuthUseCases(mock_session)

    with pytest.raises(HTTPException, match='401: Invalid special token'):
        case.user_login_part_two(email=mock_user.email, special_token='000000')

@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_login_part_two__bad_special_token_time():

    mock_user.special_token = f'123456|{(datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%d/%m/%Y, %H:%M")}'
    mock_session.query().filter_by().first.return_value = mock_user
    case = AuthUseCases(mock_session)

    with pytest.raises(HTTPException, match='401: Invalid special token'):
        case.user_login_part_two(email=mock_user.email, special_token='123456')
    mock_user.special_token = f'123456|{(datetime.now(timezone.utc) + timedelta(hours=24)).strftime("%d/%m/%Y, %H:%M")}' #Reseta ao valor original

@patch('api.cases.auth.SECRET_KEY', '3')
def test_user_login_part_two__bad_user():

    mock_session.query().filter_by().first.return_value = None
    case = AuthUseCases(mock_session)

    with pytest.raises(HTTPException, match='401: Invalid email'):
        case.user_login_part_two(email=mock_user.email, special_token='123456')
