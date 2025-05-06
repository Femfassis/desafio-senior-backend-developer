from fastapi import FastAPI
from .routes import auth_router, user_router

api = FastAPI()

@api.get("/health")
def root():
    return {'status':'online'}

api.include_router(auth_router)
api.include_router(user_router)

