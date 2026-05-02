from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.models import User, Message, Chat, ChatMember
from app.schemas.schemas import MessageResponse, MessageCreate, ChatResponse, ChatCreate
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/chats", response_model=List[ChatResponse])
async def get_chats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Chat)
        .join(ChatMember)
        .options(
            selectinload(Chat.members).selectinload(ChatMember.user),
            selectinload(Chat.messages)
        )
        .where(ChatMember.user_id == current_user.id)
        .order_by(Chat.updated_at.desc())
    )
    chats = result.scalars().unique().all()
    
    chat_responses = []
    for chat in chats:
        last_message_result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_message = last_message_result.scalar_one_or_none()
        
        unread_count_result = await db.execute(
            select(func.count(Message.id))
            .where(
                (Message.chat_id == chat.id) &
                (Message.sender_id != current_user.id) &
                (Message.is_read == False)
            )
        )
        unread_count = unread_count_result.scalar() or 0
        
        chat_data = {
            "id": chat.id,
            "name": chat.name,
            "is_group": chat.is_group,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at,
            "members": chat.members,
            "last_message": last_message,
            "unread_count": unread_count
        }
        chat_responses.append(chat_data)
    
    return chat_responses


@router.post("/chats", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat = Chat(
        name=chat_data.name if chat_data.is_group else None,
        is_group=chat_data.is_group
    )
    db.add(chat)
    await db.flush()
    
    member_ids = chat_data.member_ids or []
    if not chat_data.is_group and len(member_ids) == 1:
        existing_chat = await db.execute(
            select(Chat)
            .join(ChatMember)
            .where(
                (Chat.is_group == False) &
                (ChatMember.chat_id == Chat.id) &
                (ChatMember.user_id.in_([current_user.id, member_ids[0]]))
            )
            .group_by(Chat.id)
            .having(func.count(ChatMember.user_id) == 2)
        )
        existing = existing_chat.scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="Chat already exists")
    
    member_ids_to_add = list(set(member_ids + [current_user.id]))
    for user_id in member_ids_to_add:
        user_exists = await db.execute(select(User).where(User.id == user_id))
        if not user_exists.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        member = ChatMember(chat_id=chat.id, user_id=user_id)
        db.add(member)
    
    await db.commit()
    await db.refresh(chat)
    
    members_result = await db.execute(
        select(User)
        .join(ChatMember)
        .options(selectinload(ChatMember.user))
        .where(ChatMember.chat_id == chat.id)
    )
    members = members_result.scalars().all()
    
    return {
        "id": chat.id,
        "name": chat.name,
        "is_group": chat.is_group,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
        "members": members,
        "last_message": None,
        "unread_count": 0
    }


@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership = await db.execute(
        select(ChatMember).where(
            (ChatMember.chat_id == chat_id) &
            (ChatMember.user_id == current_user.id)
        )
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Chat not found or you're not a member")
    
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    messages = result.scalars().all()
    
    await db.execute(
        Message.__table__.update()
        .where(
            (Message.chat_id == chat_id) &
            (Message.sender_id != current_user.id) &
            (Message.is_read == False)
        )
        .values(is_read=True)
    )
    await db.commit()
    
    return messages


@router.post("/messages", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not message_data.chat_id and not message_data.receiver_id:
        raise HTTPException(status_code=400, detail="Either chat_id or receiver_id must be provided")
    
    if message_data.chat_id:
        membership = await db.execute(
            select(ChatMember).where(
                (ChatMember.chat_id == message_data.chat_id) &
                (ChatMember.user_id == current_user.id)
            )
        )
        if not membership.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Chat not found or you're not a member")
        
        message = Message(
            content=message_data.content,
            sender_id=current_user.id,
            chat_id=message_data.chat_id
        )
        
        await db.execute(
            Chat.__table__.update()
            .where(Chat.id == message_data.chat_id)
            .values(updated_at=datetime.now(timezone.utc))
        )
    else:
        receiver_exists = await db.execute(select(User).where(User.id == message_data.receiver_id))
        if not receiver_exists.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Receiver not found")
        
        message = Message(
            content=message_data.content,
            sender_id=current_user.id,
            receiver_id=message_data.receiver_id
        )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return message


@router.get("/messages/direct/{user_id}", response_model=List[MessageResponse])
async def get_direct_messages(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot get messages with yourself")
    
    result = await db.execute(
        select(Message)
        .where(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
            ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
        )
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    messages = result.scalars().all()
    
    await db.execute(
        Message.__table__.update()
        .where(
            ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id)) &
            (Message.is_read == False)
        )
        .values(is_read=True)
    )
    await db.commit()
    
    return messages


@router.patch("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = await db.execute(select(Message).where(Message.id == message_id))
    msg = message.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if msg.receiver_id != current_user.id and msg.chat_id:
        membership = await db.execute(
            select(ChatMember).where(
                (ChatMember.chat_id == msg.chat_id) &
                (ChatMember.user_id == current_user.id)
            )
        )
        if not membership.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Not authorized")
    
    msg.is_read = True
    await db.commit()
    return {"message": "Message marked as read"}


@router.get("/users/online")
async def get_online_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(User).where(User.is_active == True)
    )
    users = result.scalars().all()
    return [{"id": u.id, "username": u.username, "is_online": True} for u in users]
