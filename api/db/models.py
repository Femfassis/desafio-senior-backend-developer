from sqlalchemy import Column, String, Integer
from api.db.base import Base


class UserModel(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column('email', String, nullable=False, unique=True)
    password = Column('password', String, nullable=False)