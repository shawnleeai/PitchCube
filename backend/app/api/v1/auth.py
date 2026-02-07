"""
增强版认证路由
包含邮箱验证、密码重置、邮件通知等功能
"""

import uuid
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import logger
from app.db.mongodb import db
from app.services.email_service import (
    send_verification_email,
    send_password_reset_email,
    get_email_service,
)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# ============ 请求/响应模型 ============


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    email_verified: bool = False


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    is_active: bool
    email_verified: bool
    created_at: datetime


class VerificationRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# ============ 辅助函数 ============


def generate_verification_code() -> str:
    """生成6位数字验证码"""
    return "".join(secrets.choice(string.digits) for _ in range(6))


def generate_reset_token() -> str:
    """生成密码重置令牌"""
    return secrets.token_urlsafe(32)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ============ 数据库操作 ============


async def _create_user(user_data: UserRegister) -> dict:
    """创建用户"""
    user = {
        "id": f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "hashed_password": get_password_hash(user_data.password),
        "is_active": True,
        "email_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    if db.connected:
        await db.db.users.insert_one(user)

    return user


async def _get_user_by_email(email: str) -> Optional[dict]:
    """通过邮箱获取用户"""
    if db.connected:
        return await db.db.users.find_one({"email": email})
    return None


async def _save_verification_code(email: str, code: str, expires_minutes: int = 30):
    """保存验证码"""
    if db.connected:
        await db.db.verification_codes.insert_one(
            {
                "email": email,
                "code": code,
                "verified": False,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=expires_minutes),
            }
        )


async def _verify_code(email: str, code: str) -> bool:
    """验证验证码"""
    if not db.connected:
        return True  # 演示模式

    record = await db.db.verification_codes.find_one(
        {
            "email": email,
            "code": code,
            "verified": False,
            "expires_at": {"$gt": datetime.utcnow()},
        }
    )

    if record:
        # 标记为已使用
        await db.db.verification_codes.update_one(
            {"_id": record["_id"]}, {"$set": {"verified": True}}
        )
        return True
    return False


async def _save_reset_token(email: str, token: str, expires_hours: int = 1):
    """保存密码重置令牌"""
    if db.connected:
        await db.db.password_reset_tokens.insert_one(
            {
                "email": email,
                "token": token,
                "used": False,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=expires_hours),
            }
        )


async def _verify_reset_token(token: str) -> Optional[str]:
    """验证重置令牌，返回邮箱"""
    if not db.connected:
        return None

    record = await db.db.password_reset_tokens.find_one(
        {"token": token, "used": False, "expires_at": {"$gt": datetime.utcnow()}}
    )

    if record:
        # 标记为已使用
        await db.db.password_reset_tokens.update_one(
            {"_id": record["_id"]}, {"$set": {"used": True}}
        )
        return record["email"]
    return None


# ============ API 端点 ============


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserRegister, background_tasks: BackgroundTasks):
    """
    用户注册

    注册成功后会发送验证邮件到用户邮箱
    """
    logger.info(f"新用户注册: {user_data.email}")

    # 检查邮箱是否已存在
    if db.connected:
        existing_user = await _get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被注册"
            )

    # 创建用户
    user = await _create_user(user_data)

    # 生成验证码
    verification_code = generate_verification_code()
    await _save_verification_code(user_data.email, verification_code)

    # 发送验证邮件（后台任务）
    if get_email_service():
        background_tasks.add_task(
            send_verification_email,
            user_data.email,
            user_data.username,
            verification_code,
        )
        logger.info(f"验证邮件已发送: {user_data.email}")
    else:
        logger.warning(f"邮件服务未配置，验证码: {verification_code}")

    return UserResponse(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        full_name=user["full_name"],
        is_active=user["is_active"],
        email_verified=user["email_verified"],
        created_at=user["created_at"],
    )


@router.post("/verify-email")
async def verify_email(request: VerificationRequest):
    """验证邮箱"""
    logger.info(f"验证邮箱: {request.email}")

    # 验证验证码
    if not await _verify_code(request.email, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="验证码无效或已过期"
        )

    # 更新用户状态
    if db.connected:
        await db.db.users.update_one(
            {"email": request.email},
            {"$set": {"email_verified": True, "updated_at": datetime.utcnow()}},
        )

    return {"message": "邮箱验证成功", "email": request.email}


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest, background_tasks: BackgroundTasks
):
    """重新发送验证邮件"""
    logger.info(f"重新发送验证邮件: {request.email}")

    # 获取用户信息
    user = await _get_user_by_email(request.email)
    if not user:
        # 不泄露用户是否存在
        return {"message": "如果邮箱存在，验证邮件已发送"}

    if user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已验证"
        )

    # 生成新验证码
    verification_code = generate_verification_code()
    await _save_verification_code(request.email, verification_code)

    # 发送验证邮件
    if get_email_service():
        background_tasks.add_task(
            send_verification_email, request.email, user["username"], verification_code
        )

    return {"message": "验证邮件已发送"}


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """用户登录"""
    logger.info(f"用户登录: {credentials.email}")

    # 验证用户
    user = await _get_user_by_email(credentials.email)

    # 演示模式：支持默认账号
    if not user and credentials.email == "demo@example.com":
        user = {
            "id": "user_demo",
            "email": "demo@example.com",
            "email_verified": True,
            "hashed_password": get_password_hash("password"),
        }

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误"
        )

    # 验证密码
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误"
        )

    # 创建令牌
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    from jose import jwt

    access_token = jwt.encode(
        {
            "sub": user["id"],
            "email": user["email"],
            "exp": datetime.utcnow() + access_token_expires,
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    refresh_token = jwt.encode(
        {
            "sub": user["id"],
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=7),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        email_verified=user.get("email_verified", False),
    )


@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest, background_tasks: BackgroundTasks
):
    """请求密码重置"""
    logger.info(f"密码重置请求: {request.email}")

    user = await _get_user_by_email(request.email)

    if not user:
        # 不泄露用户是否存在
        return {"message": "如果邮箱存在，重置邮件已发送"}

    # 生成重置令牌
    reset_token = generate_reset_token()
    await _save_reset_token(request.email, reset_token)

    # 发送重置邮件
    if get_email_service():
        background_tasks.add_task(
            send_password_reset_email, request.email, user["username"], reset_token
        )
        logger.info(f"密码重置邮件已发送: {request.email}")
    else:
        # 演示模式：返回令牌
        logger.warning(f"邮件服务未配置，重置令牌: {reset_token}")

    return {"message": "如果邮箱存在，重置邮件已发送"}


@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """重置密码"""
    logger.info("密码重置确认")

    # 验证令牌
    email = await _verify_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="重置链接无效或已过期"
        )

    # 更新密码
    if db.connected:
        await db.db.users.update_one(
            {"email": email},
            {
                "$set": {
                    "hashed_password": get_password_hash(request.new_password),
                    "updated_at": datetime.utcnow(),
                }
            },
        )

    return {"message": "密码重置成功"}


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """获取当前用户（用于依赖注入）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return {"id": user_id, "email": "user@example.com"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user.get("id", "user_123"),
        email=current_user.get("email", "demo@example.com"),
        username="demo",
        full_name="Demo User",
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow(),
    )
