from pydantic import BaseModel
from fastapi import Form

"""Схема для создания пользователя"""


class UserCreate(BaseModel):
    username: str
    password: str
    password_confirm: str
    role: str = "reader"
    fullname: str | None = None
    
    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
        fullname: str | None = Form(None)
    ):
        return cls(
            username=username, 
            password=password, 
            password_confirm=password_confirm,
            fullname=fullname,
        )


"""Схема для логина"""


class UserLogin(BaseModel):
    username: str
    password: str

    @classmethod
    def as_form(cls, username: str = Form(...), password: str = Form(...)):
        return cls(username=username, password=password)
