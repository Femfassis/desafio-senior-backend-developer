from fastapi import FastAPI, status
from .routes import auth_router, user_router
from fastapi.responses import JSONResponse

api = FastAPI()

@api.get("/health")
def root():
    return JSONResponse(
        content= {'status':'online'},
        status_code=status.HTTP_200_OK
    )

api.include_router(auth_router)
api.include_router(user_router)

