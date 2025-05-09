from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from api.db.models import UserModel, TransportModel
from api.schemas import User
from passlib.context import CryptContext
from fastapi.exceptions import HTTPException
from fastapi import status
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from decouple import config
from random import randint


SECRET_KEY = config('SECRET_KEY')
ALGORITHM = 'HS256'
crypt_context = CryptContext(schemes=['sha256_crypt'])


def send_token():
    pass


class AuthUseCases:
    def __init__(self, db_session: Session):
        self.db_session = db_session


    def user_register(self, user: User):
        user = UserModel(email=user.email, password=crypt_context.hash(user.password))  
        transport = TransportModel(user=user)     
        try:
            self.db_session.add(user)
            self.db_session.add(transport)
            self.db_session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail='Email already in use'
            )
        
    def user_login(self, user: User, expires_in:int = 30):
        user_on_db = self.db_session.query(UserModel).filter_by(email=user.email).first()
        if (user_on_db is None) or (not crypt_context.verify(user.password, user_on_db.password)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        expire_date = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
        payload = {
            'sub' : user.email,
            'exp' : expire_date
        }

        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {'access_token' : access_token, 'expire_date': expire_date.isoformat()}
    

    def verify_token(self, access_token):
        try:
            data = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid access token'
            )
        user_on_db = self.db_session.query(UserModel).filter_by(email=data['sub']).first()
        if user_on_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid access token'
            )
        return user_on_db
    
    def user_login_part_one(self, user: User, special_token_duration: int = 24):
        user_on_db = self.db_session.query(UserModel).filter_by(email=user.email).first()
        if (user_on_db is None) or (not crypt_context.verify(user.password, user_on_db.password)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        special_token_1 = str(randint(100000,999999))
        special_token_2 = (datetime.now(timezone.utc) + timedelta(hours=special_token_duration)).strftime("%d/%m/%Y, %H:%M")

        special_token = f'{special_token_1}|{special_token_2}'

        user_on_db.special_token = special_token

        self.db_session.commit()

        send_token()

        return {'email' : user_on_db.email, 'special_token' : special_token_1}
        

    def user_login_part_two(self, email: str, special_token: str, expires_in:int = 30):

        user_on_db = self.db_session.query(UserModel).filter_by(email=email).first()
        if (user_on_db is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
        
        special_token_1, special_token_2 = user_on_db.special_token.split('|')

        if  datetime.now(timezone.utc) > datetime.strptime(special_token_2,"%d/%m/%Y, %H:%M").replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid special token')
        
        if special_token_1 != special_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid special token')
        
        expire_date = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
        payload = {
            'sub' : email,
            'exp' : expire_date
        }

        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {'access_token' : access_token, 'expire_date': expire_date.isoformat()}
