from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, OAuth2PasswordRequestForm

from models import UsersOrm
from .security import get_current_user_from_token, create_access_token
from repository import UserRepository, verify_password
from schemas import Token


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

security = HTTPBasic()

@router.post("/login/token", response_model=Token)
async def login(user: OAuth2PasswordRequestForm = Depends()):
    db_user = await UserRepository.find_user_by_username(user.username)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": db_user.username, "id": db_user.id, "role": db_user.role},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/test_auth_endpoint")
async def sample_endpoint_under_jwt(
    current_user: UsersOrm = Depends(get_current_user_from_token),
):
    return {"Success": True, "current_user": current_user}
