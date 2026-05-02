from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.database import get_db
from app.models.models import User, Message, Task
from app.schemas.schemas import UserResponse, MessageResponse, MessageCreate, TaskResponse, TaskCreate
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/search", response_model=List[UserResponse])
async def search_users(query: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(User).where(
            (User.username.ilike(f"%{query}%") | User.email.ilike(f"%{query}%")) &
            (User.id != current_user.id)
        ).limit(10)
    )
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
