from fastapi import FastAPI
import uvicorn
from database import create_tables, delete_tables, enable_foreign_keys
from routers.tasks_router import router as tsk_rt
from routers.users_router import router as usr_rt
from auth.auth_router import router as reg_rt
from routers.admin_router import router as adm_rt


async def lifespan(app: FastAPI):
    await enable_foreign_keys()
    print("Проверка на внешние ключи включена")
    await delete_tables()
    print("База удалена")
    await create_tables()
    print("База создана")
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan)
app.include_router(tsk_rt)
app.include_router(usr_rt)
app.include_router(reg_rt)
app.include_router(adm_rt)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)