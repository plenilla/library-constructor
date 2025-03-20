from pydantic import BaseModel
from fastapi import Form

# Схема для создания пользователя
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "reader"

# Схема для логина
class UserLogin(BaseModel):
    username: str 
    password: str 
    
    @classmethod
    def as_form(cls,
                username: str = Form(...),
                password: str = Form(...)):
        return cls(username=username, password=password)