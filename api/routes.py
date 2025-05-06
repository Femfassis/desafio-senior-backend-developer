from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .depends import get_db_session, token_verifier
from .auth import UserUseCases
from .schemas import User



auth_router = APIRouter(prefix='/auth')
user_router = APIRouter(prefix='/user', dependencies=[Depends(token_verifier)])


@auth_router.post('/register')
def user_register(user: User, db_session: Session = Depends(get_db_session)):
    case = UserUseCases(db_session=db_session)
    case.user_register(user=user)
    return Response(status_code=status.HTTP_201_CREATED)

@auth_router.post('/login')
def user_login(request_form_user: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_db_session)):
    case = UserUseCases(db_session=db_session)
    user = User(
        email=request_form_user.username,
        password=request_form_user.password
    )
    auth_data = case.user_login(user=user)
    return JSONResponse(
        content=auth_data,
        status_code=status.HTTP_200_OK
    )

@user_router.get('/documents')
def get_documents():
    return 'OK'

@user_router.post('/bot')
def ask_bot(message: str):
    return JSONResponse(content={'answer' : "Não posso responder isso ainda :("}, status_code=status.HTTP_200_OK)
