from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from src.database.database import get_db
from src.auth.models import User
from src.schemas import UserCreate, UserOut, Token
from src.auth.auth import (
    get_password_hash, authenticate_user, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
)
from src.auth.email_utils import send_welcome_email

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate,
                   background_tasks: BackgroundTasks,
                   db: AsyncSession = Depends(get_db),
                   ):
    # Проверяем, не существует ли пользователь
    result = await db.execute(select(User).where(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Создаём нового пользователя
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    background_tasks.add_task(send_welcome_email, new_user.email, new_user.username)

    return new_user


@auth_router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user