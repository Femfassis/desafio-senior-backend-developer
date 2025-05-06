from pydantic import BaseModel, field_validator
import re

class User(BaseModel):
    email: str
    password: str

    @field_validator('email')
    def validate_email(cls,value):
        if not re.match(r'^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$', value):
            raise ValueError('Invalid email')
        return value
    

