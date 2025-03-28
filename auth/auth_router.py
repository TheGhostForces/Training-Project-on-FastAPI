from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from models import UsersOrm
from .security import get_current_user_from_token, create_access_token
from repository import UserRepository, verify_password
from schemas import Token


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login/token", response_model=Token)
async def login(user: OAuth2PasswordRequestForm = Depends(), response: Response = None):
    db_user = await UserRepository.find_user_by_username(user.username)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": db_user.username, "id": db_user.id, "role": db_user.role},
        expires_delta=access_token_expires,
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Доступен только серверу
        secure=False,  # Включить в продакшене (HTTPS)
        samesite="lax"  # Предотвращает CSRF
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}

@router.get("/test_auth_endpoint")
async def sample_endpoint_under_jwt(
    current_user: UsersOrm = Depends(get_current_user_from_token),
):
    return {"Success": True, "current_user": current_user}
