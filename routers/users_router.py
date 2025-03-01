from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Security

from auth.security import get_current_user_from_token
from models import UsersOrm
from repository import UserRepository, verify_password, hash_password
from schemas import UserSchemaAdd, Universal, ChangePassword, CurrentPassword, UniversalWithId

router = APIRouter(
    prefix="/user",
)

@router.post("/register" , tags=["Registration"])
async def register(user: Annotated[UserSchemaAdd, Depends()]) -> UniversalWithId:
    existing_user = await UserRepository.find_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    id_user =  await UserRepository.add_one_user(user)
    return {"Ok":True, "id": id_user}

@router.put("/settings", tags=["Edit User"])
async def change_password(
        password: Annotated[ChangePassword, Depends()],
        current_user: UserSchemaAdd = Depends(get_current_user_from_token)
) -> UniversalWithId:
    db_user = await UserRepository.find_user_by_username(current_user.username)
    if not db_user or not verify_password(password.current_password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    await UserRepository.update_password(current_user.id, hash_password(password.new_password))
    return {"Ok": True}

@router.delete("/settings", tags=["Edit User"])
async def delete_user(
        password: Annotated[CurrentPassword, Depends()],
        current_user: UserSchemaAdd = Depends(get_current_user_from_token)
) -> UniversalWithId:
    db_user = await UserRepository.find_user_by_username(current_user.username)
    if not db_user or not verify_password(password.current_password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    await UserRepository.delete_user_by_id(current_user.id)
    return {"Ok": True}