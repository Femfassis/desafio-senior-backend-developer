from fastapi import FastAPI, status
from .routes import auth_router, user_router
from fastapi.responses import JSONResponse

api = FastAPI(title="Desafio Senior Backend Developer")

@api.get("/health", tags=['Public'])
def get_health():
    """
    Checa se a API está online.
    """
    return JSONResponse(
        content= {'status':'online'},
        status_code=status.HTTP_200_OK
    )

api.include_router(auth_router)
api.include_router(user_router)

