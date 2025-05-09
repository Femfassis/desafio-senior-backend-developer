from api.cases.user import UserUseCases
from unittest.mock import MagicMock
import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError


mock_session = MagicMock()
mock_user = MagicMock()
mock_user.id = 1
mock_document = MagicMock()
mock_document.name = 'cpf'
mock_document.number = '12345678900'

##########Add document#############
def test_add_document_OK():
    case = UserUseCases(db_session=mock_session, user=mock_user)
    case.add_document(mock_document)

    assert mock_session.add.assert_called_once
    assert mock_session.add.assert_called_once

def test_add_document_bad_integrity():
    case = UserUseCases(db_session=mock_session, user=mock_user)
    mock_session.commit.side_effect = IntegrityError('', '', '')

    with pytest.raises(HTTPException, match='Document already in use'):
        case.add_document(mock_document)
    mock_session.reset_mock(side_effect=True) #Reseta o side_effetct

