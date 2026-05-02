from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.models import News, User
from app.schemas.schemas import NewsResponse, NewsCreate
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/news", response_model=List[NewsResponse])
async def get_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(News).where(News.is_published == True)
    query = query.order_by(desc(News.published_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    news_list = result.scalars().all()
    
    return [
        {
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "author_id": n.author_id,
            "author_username": n.author.username if n.author else None,
            "is_published": n.is_published,
            "published_at": n.published_at,
            "created_at": n.created_at,
            "updated_at": n.updated_at
        }
        for n in news_list
    ]


@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_news_item(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    if not news.is_published:
        raise HTTPException(status_code=403, detail="News is not published")
    
    return {
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "author_id": news.author_id,
        "author_username": news.author.username if news.author else None,
        "is_published": news.is_published,
        "published_at": news.published_at,
        "created_at": news.created_at,
        "updated_at": news.updated_at
    }


@router.post("/news", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(
    news_data: NewsCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    news = News(
        title=news_data.title,
        content=news_data.content,
        author_id=current_user.id,
        is_published=False
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)
    
    return {
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "author_id": news.author_id,
        "author_username": current_user.username,
        "is_published": news.is_published,
        "published_at": news.published_at,
        "created_at": news.created_at,
        "updated_at": news.updated_at
    }


@router.put("/news/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    news_data: NewsCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    if news.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    news.title = news_data.title
    news.content = news_data.content
    news.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(news)
    
    return {
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "author_id": news.author_id,
        "author_username": current_user.username,
        "is_published": news.is_published,
        "published_at": news.published_at,
        "created_at": news.created_at,
        "updated_at": news.updated_at
    }


@router.post("/news/{news_id}/publish", response_model=NewsResponse)
async def publish_news(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    if news.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    news.is_published = True
    news.published_at = datetime.now(timezone.utc)
    news.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(news)
    
    return {
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "author_id": news.author_id,
        "author_username": current_user.username,
        "is_published": news.is_published,
        "published_at": news.published_at,
        "created_at": news.created_at,
        "updated_at": news.updated_at
    }


@router.delete("/news/{news_id}")
async def delete_news(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    if news.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.delete(news)
    await db.commit()
    
    return {"message": "News deleted successfully"}
