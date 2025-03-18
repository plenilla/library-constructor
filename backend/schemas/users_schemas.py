from pydantic import BaseModel, ConfigDict 

# Схема для создания пользователя
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "reader"

# Схема для логина
class UserLogin(BaseModel):
    username: str 
    password: str 
    
    model_config = ConfigDict(
        from_attributes=True, # Для работы с ОРМ
        json_schema_extra={
            "examples":[{
                "username": "john_doe",
                "password": "securepassword123"
            }]
        }
    )
    
    
