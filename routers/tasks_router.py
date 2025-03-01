from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from auth.security import get_current_user_from_token, require_role
from models import UsersOrm
from repository import TaskRepository
from schemas import TaskSchemaAdd, TaskSchema, Universal, UserSchemaAdd, TaskDelete, UniversalWithId

router = APIRouter(
    prefix="/task",
    tags=["Tasks"]
)

@router.post("")
async def add_task_current_user(
        task: Annotated[TaskSchemaAdd, Depends()],
        current_user: UserSchemaAdd = Depends(get_current_user_from_token)
) -> UniversalWithId:
    task_id = await TaskRepository.add_one_task(task, current_user.id)
    return {'Ok': True, "id": task_id}

@router.get("")
async def get_all_tasks_current_user(current_user: UserSchemaAdd = Depends(get_current_user_from_token)) -> list[TaskSchema]:
    tasks = await TaskRepository.find_all_tasks(current_user.id)
    return tasks

@router.delete("")
async def delete_task(
        task: Annotated[TaskDelete, Depends()],
        current_user: UserSchemaAdd = Depends(get_current_user_from_token),
        _: UsersOrm = Depends(require_role("user"))
) -> Universal:
    received_task = await TaskRepository.get_task_current_user_by_id(task.id, current_user.id)
    if not received_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    await TaskRepository.delete_task_by_id(task.id, current_user.id)
    return {"Ok": True}

