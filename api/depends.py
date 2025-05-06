from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from .auth import UserUseCases
from .db.connection import session
from sqlalchemy.orm import Session

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_db_session():
    try:
        new_session = session()
        yield new_session
    finally:
        new_session.close()

def token_verifier(db_session: Session = Depends(get_db_session), token = Depends(oauth_scheme)):
    case = UserUseCases(db_session=db_session)
    case.verify_token(access_token=token)


    