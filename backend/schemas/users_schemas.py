from pydantic import BaseModel

# Схема для создания пользователя
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "reader"

# Схема для логина
class UserLogin(BaseModel):
    username: str
    password: str
