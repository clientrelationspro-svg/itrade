"""
认证路由 - JWT 登录/注册
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
from jose import JWTError, jwt
from app.database import get_db
from app.models import User
from app.config import get_settings
from app.schemas import LoginRequest, TokenResponse

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["认证"])

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="未提供认证信息")
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证令牌")
    except JWTError:
        raise HTTPException(status_code=401, detail="认证令牌无效或已过期")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="用户已被禁用")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="用户已被禁用")

    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    return TokenResponse(access_token=access_token)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
    }


@router.post("/init-admin")
async def init_admin(db: AsyncSession = Depends(get_db)):
    """初始化管理员账号（仅当无用户时可用）"""
    result = await db.execute(select(User))
    existing = result.scalars().all()
    if existing:
        raise HTTPException(status_code=400, detail="已存在用户，无法初始化")

    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        full_name="系统管理员",
        role="admin",
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    await db.refresh(admin)
    return {"message": "管理员账号创建成功", "username": "admin", "password": "admin123"}
