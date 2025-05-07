from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from api.db.base import Base


class UserModel(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True) #Escolhido como chave primária pois o email pode resultar em problemas de performance, além da possibilidade de troca de email no futuro
    email = Column('email', String, nullable=False, unique=True)
    password = Column('password', String, nullable=False)
    transport = relationship('TransportModel', back_populates='user', uselist=False)
    documents = relationship('DocumentModel')

class TransportModel(Base):
    __tablename__ = 'transport'
    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True)
    balance = Column('balance', Float,  default=0)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('UserModel', back_populates='transport')

class DocumentModel(Base):
    __tablename__ = 'documents'
    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(ForeignKey('users.id'))
    number = Column('number', String, nullable=False, unique=True)
    name = Column('name', String, nullable=False)