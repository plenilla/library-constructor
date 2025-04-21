# admin.py
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from pydantic import BaseModel
from .models import User, UserRole
from ..core import templates, get_db


router = APIRouter()


# Функция для проверки, что текущий пользователь – администратор
def check_admin(request: Request):
    if request.session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")


# Endpoint для отдачи статической панели админа (файл adminpanel.html должен лежать в каталоге frontend)
@router.get("/dashboard/", response_class=HTMLResponse)
async def item_page(request: Request):
    """Это страница со списком всех пользователей"""
    return templates.TemplateResponse("adminpanel.html", {"request": request})


# Endpoint для получения списка пользователей в JSON
@router.get("/dashboard/users", response_class=JSONResponse)
async def get_users(request: Request, db: AsyncSession = Depends(get_db)):
    check_admin(request)
    result = await db.execute(select(User))
    users = result.scalars().all()
    users_list = [
        {"id": user.id, "username": user.username, "role": user.role.value}
        for user in users
    ]
    return JSONResponse(content=users_list)


# Схема для обновления пользователя


# Pydantic-схема запроса
class UserUpdate(BaseModel):
    username: str
    role: str


# Endpoint для обновления данных пользователя (используем JSON)
@router.put("/dashboard/users/{user_id}")
async def update_user(
    user_id: int, update: UserUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user.username = update.username
        user.role = update.role

        await db.commit()
        await db.refresh(user)

        return {"id": user.id, "username": user.username, "role": user.role}

    except Exception as e:
        print("Ошибка обновления пользователя:", e)
        raise HTTPException(
            status_code=500, detail="Ошибка сервера при обновлении пользователя"
        )


# Endpoint для удаления пользователя
@router.delete("/dashboard/users/{user_id}", response_class=JSONResponse)
async def delete_user(
    user_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    check_admin(request)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    stmt = delete(User).where(User.id == user_id)
    await db.execute(stmt)
    await db.commit()
    return JSONResponse(content={"message": "User deleted"})
