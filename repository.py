from passlib.context import CryptContext
from sqlalchemy import select, update, delete
import asyncio

from database import new_session
from models import TasksOrm, UsersOrm
from schemas import TaskSchemaAdd, UserSchemaAdd, TaskSchema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class TaskRepository:
    @classmethod
    async def add_one_task(cls, data: TaskSchemaAdd, id_user: int):
        async with new_session() as session:
            task_dict = data.model_dump()
            task_dict["id_user"] = id_user

            task = TasksOrm(**task_dict)
            session.add(task)
            await session.flush()
            await session.commit()
            return task.id

    @classmethod
    async def find_all_tasks(cls, user_id) -> list[TaskSchema]:
        async with new_session() as session:
            query = select(TasksOrm).filter(TasksOrm.id_user == user_id)
            result = await session.execute(query)
            task_models = result.scalars().all()
            return task_models

    @classmethod
    async def get_task_current_user_by_id(cls, task_id: int, user_id: int):
        async with new_session() as session:
            query = select(TasksOrm).where(TasksOrm.id == task_id).where(TasksOrm.id_user == user_id)
            task_result = await session.execute(query)
            return task_result.scalar_one_or_none()

    @classmethod
    async def delete_task_by_id(cls, task_id: int, user_id) -> None:
        async with new_session() as session:
            query = delete(TasksOrm).where(TasksOrm.id == task_id).where(TasksOrm.id_user == user_id)
            await session.execute(query)
            await session.commit()

class UserRepository:
    @classmethod
    async def add_one_user(cls, data: UserSchemaAdd):
        async with new_session() as session:
            user_dict = data.model_dump()

            loop = asyncio.get_running_loop()
            user_dict['password'] = await loop.run_in_executor(None, hash_password, user_dict['password'])
            user_dict['role'] = "user"
            user = UsersOrm(**user_dict)
            session.add(user)
            await session.flush()
            await session.commit()
            return user.id

    @classmethod
    async def find_user_by_username(cls, username: str):
        async with new_session() as session:
            query = select(UsersOrm).where(UsersOrm.username == username)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def update_password(cls, user_id: int, new_password: str) -> None:
        async with new_session() as session:
            query = (
                update(UsersOrm)
                .where(UsersOrm.id == user_id)
                .values(password=new_password)
            )
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete_user_by_id(cls, user_id: int) -> None:
        async with new_session() as session:
            query = (
                delete(UsersOrm)
                .where(UsersOrm.id == user_id)
            )
            await session.execute(query)
            await session.commit()

class AdminRepository:
    @classmethod
    async def find_user_by_role(cls, role: str):
        async with new_session() as session:
            result = await session.execute(
                select(UsersOrm).where(UsersOrm.role == role))
            return result.scalars().first()

    @classmethod
    async def add_one_admin(cls, data: UserSchemaAdd):
        async with new_session() as session:
            admin_dict = data.model_dump()

            loop = asyncio.get_running_loop()
            admin_dict['password'] = await loop.run_in_executor(None, hash_password, admin_dict['password'])
            admin_dict["role"] = "admin"
            admin = UsersOrm(**admin_dict)
            session.add(admin)
            await session.flush()
            await session.commit()
            return admin.id

    @classmethod
    async def get_all_tasks(cls):
        async with new_session() as session:
            query = select(TasksOrm)
            result = await session.execute(query)
            task_models = result.scalars().all()
            return task_models

    @classmethod
    async def get_all_users(cls):
        async with new_session() as session:
            query = select(UsersOrm)
            result = await session.execute(query)
            user_models = result.scalars().all()
            return user_models

    @classmethod
    async def delete_user_by_username(cls, user_username: int):
        async with new_session() as session:
            query = (
                delete(UsersOrm)
                .where(UsersOrm.username == user_username)
            )
            await session.execute(query)
            await session.commit()