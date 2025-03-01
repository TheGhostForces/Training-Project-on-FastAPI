from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from auth.security import get_current_user_from_token, require_role
from models import UsersOrm
from repository import AdminRepository
from schemas import UserSchemaAdd, TaskSchema, UserSchema, UserDelete, Universal, UniversalWithId

router = APIRouter(
    prefix="/admin",
    tags=["Admin_Tools"]
)

@router.post("")
async def add_one_admin_user(user: Annotated[UserSchemaAdd, Depends()]) -> UniversalWithId:
    existing_admin = await AdminRepository.find_user_by_role("admin")
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin user already exists"
        )
    id_admin = await AdminRepository.add_one_admin(user)
    return {"Ok": True, "id": id_admin}

@router.get("/tasks")
async def get_all_tasks(
        current_user: UserSchemaAdd = Depends(get_current_user_from_token),
        _: UsersOrm = Depends(require_role("admin"))
                        ) -> list[TaskSchema]:
    tasks = await AdminRepository.get_all_tasks()
    return tasks

@router.get("/users")
async def get_all_users(
        current_user: UserSchemaAdd = Depends(get_current_user_from_token),
        _: UsersOrm = Depends(require_role("admin"))
                        ) -> list[UserSchema]:
    users = await AdminRepository.get_all_users()
    return users

@router.delete("/")
async def delete_user(
        user: Annotated[UserDelete, Depends()],
        current_user: UserSchemaAdd = Depends(get_current_user_from_token),
        _: UsersOrm = Depends(require_role("admin"))
) -> Universal:
    await AdminRepository.delete_user_by_username(user.username)
    return {"Ok": True}