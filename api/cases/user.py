from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from api.schemas import Document
from api.db.models import DocumentModel
from fastapi.exceptions import HTTPException
from fastapi import status



class UserUseCases:
    def __init__(self, db_session: Session, user):
        self.db_session = db_session
        self.user = user


    def add_document(self, document: Document):
        document = DocumentModel(name = document.name, number = document.number, user_id = self.user.id)
        try:

            self.db_session.add(document)
            self.db_session.commit()
            
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail='Document already in use'
            )
        
    def get_documents(self):
        documents = self.db_session.query(DocumentModel).filter_by(user_id=self.user.id).all()
        documents = [{'name': document.name, 'number' : document.number} for document in documents]
        return documents