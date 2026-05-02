from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import re

from app.db.database import get_db
from app.models.models import User, EmailCode, LoginAttempt
from app.schemas.schemas import (
    UserCreate, UserLogin, UserResponse, Token, RefreshTokenRequest,
    EmailVerifyRequest, PasswordResetRequest, PasswordResetConfirm, MessageResponse
)
from app.core.config import settings
from app.services.password_service import PasswordService
from app.services.email_service import EmailService

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password[:72], hashed_password)
    except Exception:
        return False


def validate_password(password: str) -> tuple[bool, str]:
    return PasswordService.validate_password(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def check_login_attempts(ip: str, email: str, db: AsyncSession) -> bool:
    window_start = datetime.now(timezone.utc) - timedelta(minutes=settings.LOGIN_ATTEMPT_WINDOW_MINUTES)
    result = await db.execute(
        select(func.count(LoginAttempt.id))
        .where(
            LoginAttempt.ip_address == ip,
            LoginAttempt.attempted_at >= window_start,
            LoginAttempt.success == False
        )
    )
    failed_attempts = result.scalar() or 0
    return failed_attempts < settings.MAX_LOGIN_ATTEMPTS


async def record_login_attempt(ip: str, email: str, success: bool, db: AsyncSession):
    attempt = LoginAttempt(
        ip_address=ip,
        email=email,
        success=success
    )
    db.add(attempt)
    await db.commit()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    is_valid, error_message = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    result = await db.execute(select(User).where((User.username == user_data.username) | (User.email == user_data.email)))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    verification_code = EmailService.generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    
    temp_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_verified=False
    )
    db.add(temp_user)
    await db.commit()
    await db.refresh(temp_user)
    
    email_code = EmailCode(
        email=user_data.email,
        code=verification_code,
        expires_at=expires_at
    )
    db.add(email_code)
    
    html_content = EmailService.get_verification_email_html(verification_code, settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    await EmailService.send_email(user_data.email, "Подтверждение email", html_content)
    
    await db.commit()
    
    return temp_user


@router.post("/login", response_model=Token)
async def login(request: Request, credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    
    can_login = await check_login_attempts(client_ip, credentials.login, db)
    if not can_login:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again in {settings.LOGIN_ATTEMPT_WINDOW_MINUTES} minutes."
        )
    
    result = await db.execute(select(User).where((User.username == credentials.login) | (User.email == credentials.login)))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        await record_login_attempt(client_ip, credentials.login, False, db)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    await record_login_attempt(client_ip, credentials.login, True, db)
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    refresh_token = req.refresh_token
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token required")
    
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    new_access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/resend-code")
async def resend_code(req: EmailVerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    verification_code = EmailService.generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    
    email_code = EmailCode(
        email=req.email,
        code=verification_code,
        expires_at=expires_at
    )
    db.add(email_code)
    await db.commit()
    
    html_content = EmailService.get_verification_email_html(verification_code, settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    sent = await EmailService.send_email(req.email, "Подтверждение email", html_content)
    
    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    return {"message": "Verification code sent"}


@router.post("/confirm-email")
async def confirm_email(req: EmailVerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    now = datetime.now(timezone.utc)
    code_result = await db.execute(
        select(EmailCode)
        .where(
            EmailCode.email == req.email,
            EmailCode.code == req.code,
            EmailCode.is_used == False,
            EmailCode.expires_at > now
        )
        .order_by(EmailCode.created_at.desc())
        .limit(1)
    )
    email_code = code_result.scalar_one_or_none()
    
    if not email_code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    email_code.is_used = True
    user.is_verified = True
    await db.commit()
    
    return {"message": "Email verified successfully"}


@router.post("/reset-password-request")
async def reset_password_request(req: EmailVerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    
    if not user:
        return {"message": "If email exists, reset code has been sent"}
    
    reset_code = EmailService.generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    
    email_code = EmailCode(
        email=req.email,
        code=reset_code,
        expires_at=expires_at
    )
    db.add(email_code)
    await db.commit()
    
    html_content = EmailService.get_reset_password_email_html(reset_code, settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    await EmailService.send_email(req.email, "Сброс пароля", html_content)
    
    return {"message": "If email exists, reset code has been sent"}


@router.post("/reset-password-confirm")
async def reset_password_confirm(req: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    is_valid, error_message = validate_password(req.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    now = datetime.now(timezone.utc)
    code_result = await db.execute(
        select(EmailCode)
        .where(
            EmailCode.email == req.email,
            EmailCode.code == req.code,
            EmailCode.is_used == False,
            EmailCode.expires_at > now
        )
        .order_by(EmailCode.created_at.desc())
        .limit(1)
    )
    email_code = code_result.scalar_one_or_none()
    
    if not email_code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    user.hashed_password = hash_password(req.new_password)
    email_code.is_used = True
    await db.commit()
    
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    is_valid, error_message = validate_password(new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    current_user.hashed_password = hash_password(new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.put("/profile")
async def update_profile(
    first_name: str = None,
    last_name: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if first_name is not None:
        current_user.first_name = first_name
    if last_name is not None:
        current_user.last_name = last_name
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user
