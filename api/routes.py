from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .depends import get_db_session, token_verifier
from .cases.auth import AuthUseCases
from .cases.user import UserUseCases
from .schemas import User, Document
from math import floor
from pydantic import ValidationError

###############Auth paths#####################
auth_router = APIRouter(prefix='/auth', tags=['Auth'])

@auth_router.post('/register')
def user_register(user: User, db_session: Session = Depends(get_db_session)):
    """
    Registra um novo usuário dados email e senha.
    """
    case = AuthUseCases(db_session=db_session)
    case.user_register(user=user)
    return Response(status_code=status.HTTP_201_CREATED)

@auth_router.post('/login')
def user_login(request_form_user: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_db_session)):
    """
    Faz login de um usuário dado email e senha. Retorna token de acesso.
    """
    case = AuthUseCases(db_session=db_session)

    try: 
        user = User(
            email=request_form_user.username,
            password=request_form_user.password
        )
    except ValidationError:
        return JSONResponse(content={'detail' : "Email inválido"}, status_code=status.HTTP_400_BAD_REQUEST)
    

    auth_data = case.user_login(user=user)
    return JSONResponse(
        content=auth_data,
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/login_part_one')
def user_login_part_one(request_form_user: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_db_session)):
    """
    Primeiro passo de login em duas etapas. Toma email e senha como entrada, retornando o email e mandando um token especial para o usuário de alguma
    forma alternativa (como email ou dispositivo móvel). Nesta simulação, retorna o token no corpo da resposta pois os métodos corretos são inválidos.
    """
    case = AuthUseCases(db_session=db_session)
    try: 
        user = User(
            email=request_form_user.username,
            password=request_form_user.password
        )
    except ValidationError:
        return JSONResponse(content={'detail' : "Email inválido"}, status_code=status.HTTP_400_BAD_REQUEST)
    
    auth_data = case.user_login_part_one(user=user)
    return JSONResponse(
        content=auth_data,
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/login_part_two')
def user_login_part_one(email: str, special_token: str, db_session: Session = Depends(get_db_session)):
    """
    Segundo passo de login em duas etapas. Nesta, é requerido um email e um token especial enviado ao usuário na primeira etapa de login. 
    Retorna um token de acesso.
    """
    case = AuthUseCases(db_session=db_session)
    auth_data = case.user_login_part_two(email=email, special_token=special_token)

    return JSONResponse(
        content=auth_data,
        status_code=status.HTTP_200_OK
    )



###############User paths#####################
user_router = APIRouter(prefix='/user', dependencies=[Depends(token_verifier)], tags=['User'])

@user_router.post('/bot')
def ask_bot(message: str):
    """
    Manda uma mensagem a um robô e ele finge responder.
    """
    return JSONResponse(content={'answer' : "Não posso responder isso ainda :("}, status_code=status.HTTP_200_OK)

@user_router.get('/balance')
def get_transport_balance(db_session: Session = Depends(get_db_session), token_verify = Depends(token_verifier)):
    """
    Retorna o saldo do vale transporte do usuário.
    """
    return JSONResponse(content={'balance':token_verify.transport.balance}, status_code=status.HTTP_200_OK)

@user_router.post('/balance')
def post_transport_balance(value: float, db_session: Session = Depends(get_db_session), token_verify = Depends(token_verifier)):
    """
    Adiciona valor ao vale transporte do usuário.
    """
    value = max(0, floor(100*value)/100.0) #Garante que é um valor válido de reais
    new_balance = round(token_verify.transport.balance+value,2)
    token_verify.transport.balance = new_balance
    db_session.commit()
    return JSONResponse(content={'balance':token_verify.transport.balance}, status_code=status.HTTP_200_OK)


@user_router.post('/documents')
def post_document(document: Document, db_session: Session = Depends(get_db_session), token_verify = Depends(token_verifier)):
    """
    Adiciona documento à lista de documentos do usuário.
    """
    case = UserUseCases(db_session= db_session, user=token_verify)
    case.add_document(document)
    return Response(status_code=status.HTTP_200_OK)


@user_router.get('/documents')
def get_document(db_session: Session = Depends(get_db_session), token_verify = Depends(token_verifier)):
    """
    Retorna lista de documentos do usuário.
    """
    case = UserUseCases(db_session= db_session, user=token_verify)
    documents = case.get_documents()
    return JSONResponse(content=documents, status_code=status.HTTP_200_OK)
