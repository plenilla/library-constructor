from pydantic import BaseModel
from fastapi import Form
from pydantic import BaseModel, ConfigDict, validator, Field
import re

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


class UserSelfUpdate(BaseModel):
    username: str | None = None
    fullname: str | None = None

    @validator("fullname")
    def validate_fullname(cls, v):
        if v is None:
            return v
        pattern = r"^[А-ЯЁ][а-яё]+ [А-ЯЁ]\.[А-ЯЁ]\.$"
        if not re.match(pattern, v):
            raise ValueError("ФИО должно быть в формате Фамилия И.О. (например, Федоров Н.С.)")
        return v
    
    
class AdminUserUpdate(BaseModel):
    username: str | None = None
    fullname: str | None = None
    role: str | None = None

    @validator("fullname")
    def validate_fullname(cls, v):
        if v is None:
            return v
        pattern = r"^[А-ЯЁ][а-яё]+ [А-ЯЁ]\.[А-ЯЁ]\.$"
        if not re.match(pattern, v):
            raise ValueError("ФИО должно быть в формате Фамилия И.О. (например, Федоров Н.С.)")
        return v