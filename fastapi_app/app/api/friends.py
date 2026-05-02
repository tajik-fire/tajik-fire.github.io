from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.models import User, Friendship, Notification
from app.schemas.schemas import UserResponse, FriendshipResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/request/{friend_id}", response_model=FriendshipResponse)
async def send_friend_request(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if friend_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")
    
    friend = await db.get(User, friend_id)
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing = await db.execute(
        select(Friendship).where(
            or_(
                (Friendship.user1_id == current_user.id) & (Friendship.user2_id == friend_id),
                (Friendship.user1_id == friend_id) & (Friendship.user2_id == current_user.id)
            )
        )
    )
    existing_friendship = existing.scalar_one_or_none()
    
    if existing_friendship:
        if existing_friendship.status == "accepted":
            raise HTTPException(status_code=400, detail="Already friends")
        elif existing_friendship.status == "requested":
            if existing_friendship.user1_id == current_user.id:
                raise HTTPException(status_code=400, detail="Request already sent")
            else:
                existing_friendship.status = "accepted"
                existing_friendship.updated_at = datetime.now(timezone.utc)
                await db.commit()
                await db.refresh(existing_friendship)
                
                notification = Notification(
                    user_id=friend_id,
                    title="Friend Request Accepted",
                    message=f"{current_user.username} accepted your friend request",
                    notification_type="friendship"
                )
                db.add(notification)
                await db.commit()
                
                return {
                    "id": existing_friendship.id,
                    "user_id": existing_friendship.user1_id,
                    "friend_id": existing_friendship.user2_id,
                    "friend_username": friend.username,
                    "friend_avatar": friend.avatar_url,
                    "status": "accepted",
                    "created_at": existing_friendship.created_at,
                    "updated_at": existing_friendship.updated_at
                }
        elif existing_friendship.status == "blocked":
            raise HTTPException(status_code=400, detail="Cannot send request to blocked user")
    
    friendship = Friendship(
        user1_id=current_user.id,
        user2_id=friend_id,
        status="requested"
    )
    db.add(friendship)
    
    notification = Notification(
        user_id=friend_id,
        title="New Friend Request",
        message=f"{current_user.username} sent you a friend request",
        notification_type="friendship"
    )
    db.add(notification)
    
    await db.commit()
    await db.refresh(friendship)
    
    return {
        "id": friendship.id,
        "user_id": friendship.user1_id,
        "friend_id": friendship.user2_id,
        "friend_username": friend.username,
        "friend_avatar": friend.avatar_url,
        "status": friendship.status,
        "created_at": friendship.created_at,
        "updated_at": friendship.updated_at
    }


@router.delete("/request/{friend_id}")
async def cancel_friend_request(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friendship = await db.execute(
        select(Friendship).where(
            (Friendship.user1_id == current_user.id) & (Friendship.user2_id == friend_id) & (Friendship.status == "requested")
        )
    )
    fs = friendship.scalar_one_or_none()
    
    if not fs:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    await db.delete(fs)
    await db.commit()
    return {"message": "Friend request cancelled"}


@router.post("/accept/{friend_id}")
async def accept_friend_request(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friendship = await db.execute(
        select(Friendship).where(
            (Friendship.user1_id == friend_id) & (Friendship.user2_id == current_user.id) & (Friendship.status == "requested")
        )
    )
    fs = friendship.scalar_one_or_none()
    
    if not fs:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    fs.status = "accepted"
    fs.updated_at = datetime.now(timezone.utc)
    
    notification = Notification(
        user_id=friend_id,
        title="Friend Request Accepted",
        message=f"{current_user.username} accepted your friend request",
        notification_type="friendship"
    )
    db.add(notification)
    
    await db.commit()
    
    friend = await db.get(User, friend_id)
    return {
        "id": fs.id,
        "user_id": fs.user1_id,
        "friend_id": fs.user2_id,
        "friend_username": current_user.username,
        "friend_avatar": current_user.avatar_url,
        "status": "accepted",
        "created_at": fs.created_at,
        "updated_at": fs.updated_at
    }


@router.post("/reject/{friend_id}")
async def reject_friend_request(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friendship = await db.execute(
        select(Friendship).where(
            (Friendship.user1_id == friend_id) & (Friendship.user2_id == current_user.id) & (Friendship.status == "requested")
        )
    )
    fs = friendship.scalar_one_or_none()
    
    if not fs:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    await db.delete(fs)
    await db.commit()
    return {"message": "Friend request rejected"}


@router.delete("/{friend_id}")
async def remove_friend(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friendship = await db.execute(
        select(Friendship).where(
            or_(
                (Friendship.user1_id == current_user.id) & (Friendship.user2_id == friend_id),
                (Friendship.user1_id == friend_id) & (Friendship.user2_id == current_user.id)
            )
        ) & (Friendship.status == "accepted")
    )
    fs = friendship.scalar_one_or_none()
    
    if not fs:
        raise HTTPException(status_code=404, detail="Friendship not found")
    
    await db.delete(fs)
    await db.commit()
    return {"message": "Friend removed"}


@router.get("/list", response_model=List[FriendshipResponse])
async def get_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friendships = await db.execute(
        select(Friendship).where(
            ((Friendship.user1_id == current_user.id) | (Friendship.user2_id == current_user.id)) &
            (Friendship.status == "accepted")
        )
    )
    fs_list = friendships.scalars().all()
    
    result = []
    for fs in fs_list:
        friend_id = fs.user2_id if fs.user1_id == current_user.id else fs.user1_id
        friend = await db.get(User, friend_id)
        if friend:
            result.append({
                "id": fs.id,
                "user_id": current_user.id,
                "friend_id": friend_id,
                "friend_username": friend.username,
                "friend_avatar": friend.avatar_url,
                "status": "accepted",
                "created_at": fs.created_at,
                "updated_at": fs.updated_at
            })
    
    return result


@router.get("/requests", response_model=List[FriendshipResponse])
async def get_friend_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friendships = await db.execute(
        select(Friendship).where(
            (Friendship.user2_id == current_user.id) & (Friendship.status == "requested")
        )
    )
    fs_list = friendships.scalars().all()
    
    result = []
    for fs in fs_list:
        requester = await db.get(User, fs.user1_id)
        if requester:
            result.append({
                "id": fs.id,
                "user_id": fs.user1_id,
                "friend_id": fs.user2_id,
                "friend_username": requester.username,
                "friend_avatar": requester.avatar_url,
                "status": "requested",
                "created_at": fs.created_at,
                "updated_at": fs.updated_at
            })
    
    return result
