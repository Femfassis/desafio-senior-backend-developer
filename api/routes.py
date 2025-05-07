from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .depends import get_db_session, token_verifier
from .cases.auth import AuthUseCases
from .cases.user import UserUseCases
from .schemas import User, Document
from math import floor

###############Auth paths#####################
auth_router = APIRouter(prefix='/auth')

@auth_router.post('/register')
def user_register(user: User, db_session: Session = Depends(get_db_session)):
    case = AuthUseCases(db_session=db_session)
    case.user_register(user=user)
    return Response(status_code=status.HTTP_201_CREATED)

@auth_router.post('/login')
def user_login(request_form_user: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_db_session)):
    case = AuthUseCases(db_session=db_session)
    user = User(
        email=request_form_user.username,
        password=request_form_user.password
    )
    auth_data = case.user_login(user=user)
    return JSONResponse(
        content=auth_data,
        status_code=status.HTTP_200_OK
    )


###############User paths#####################
user_router = APIRouter(prefix='/user', dependencies=[Depends(token_verifier)])

@user_router.post('/bot')
def ask_bot(message: str):
    return JSONResponse(content={'answer' : "Não posso responder isso ainda :("}, status_code=status.HTTP_200_OK)

@user_router.get('/balance')
def get_transport_balance(db_session: Session = Depends(get_db_session), token_verify = Depends(token_verifier)):
    return JSONResponse(content={'balance':token_verify.transport.balance}, status_code=status.HTTP_200_OK)

@user_router.post('/balance')
def get_transport_balance(value: float, db_session: Session = Depends(get_db_session), token_verify = Depends(token_verifier)):
    value = max(0, floor(100*value)/100.0) #Garante que é um valor válido de reais
    new_balance = round(token_verify.transport.balance+value,2)
    token_verify.transport.balance = new_balance
    db_session.commit()
    return JSONResponse(content={'balance':token_verify.transport.balance}, status_code=status.HTTP_200_OK)


@user_router.post('/documents')
def post_document(document: Document, db_session: Session = Depends(get_db_session), token_verify = Depends(token_verifier)):
    case = UserUseCases(db_session= db_session, user=token_verify)
    case.add_document(document)
    return Response(status_code=status.HTTP_200_OK)


@user_router.get('/documents')
def post_document(db_session: Session = Depends(get_db_session), token_verify = Depends(token_verifier)):
    case = UserUseCases(db_session= db_session, user=token_verify)
    documents = case.get_documents()
    return JSONResponse(content=documents, status_code=status.HTTP_200_OK)
