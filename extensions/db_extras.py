import asyncio
from contextlib import contextmanager, asynccontextmanager
import glob
import importlib
import os
import re

# from typing import Generator, AsyncGenerator
from typing import AsyncGenerator

# from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session, async_sessionmaker

# from sqlalchemy.orm import sessionmaker, scoped_session

from config import settings

# engine = create_engine(
#     settings.SQLALCHEMY_DATABASE_URI,
#     echo=settings.SQLALCHEMY_ECHO,
#     pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
#     pool_size=settings.SQLALCHEMY_POOL_SIZE,
#     pool_timeout=settings.SQLALCHEMY_POOL_TIMEOUT,
#     max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
# )
# # logger.debug(SQLALCHEMY_DATABASE_URI)
# # expire_on_commit 为 False，标识不清空session，但会引发查询和更新之间的缓存问题，可能需要手动调用session.expire_all
# # 用scoped_session管理全局session
# SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False))
# # db = SessionLocal()

async_engine = create_async_engine(
    settings.ASYNC_SQLALCHEMY_DATABASE_URI,
    echo=settings.SQLALCHEMY_ECHO,
    pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
    pool_size=settings.SQLALCHEMY_POOL_SIZE,
    pool_timeout=settings.SQLALCHEMY_POOL_TIMEOUT,
    max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
)

AsyncSessionLocal = async_scoped_session(
    async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession), scopefunc=asyncio.current_task
)


def import_all_models(models_path=os.path.join(settings.ROOT_PATH, 'app', 'models', '*.py')):
    model_files = glob.glob(models_path)

    for file in model_files:
        # print(file)
        # module_name = file[:-3].replace(f'{AllConfig.ROOT_PATH}/', '').replace('/', '.')
        module_name = file[:-3].replace(settings.ROOT_PATH, '')
        module_name = re.sub(r'[\\\/]', '.', module_name[1:])
        # print(module_name)
        if module_name.split('.')[-1] in ('__init__', 'base'):
            continue
        mod = importlib.import_module(module_name)


# 定义数据库会话上下文管理器，用于确保每个操作都在正确的会话上下文中执行
# @contextmanager
# def get_db_session() -> Generator:
#     session = None
#     try:
#         session = SessionLocal()
#         yield session
#         session.commit()  # 提交事务
#         # session.expire_all()  # 清理缓存
#         # 实例的属性时出现了DetachedInstanceError，这通常发生在实例已经分离（detached）于其关联的会话（session）之外，导致无法访问其属性。
#         # 通常情况下，当从数据库中查询一个对象并将其传递到其他地方时，会话会自动将其与数据库关联起来。但是，在某些情况下，对象可能会分离（例如，会话结束时或手动调用expunge_all()方法时）。
#     except Exception as e:
#         session.rollback()  # 回滚事务
#         raise e
#     finally:
#         if session:
#             session.close()  # 关闭会话


@asynccontextmanager
async def get_db_session_async() -> AsyncGenerator:
    session = None
    try:
        session = AsyncSessionLocal
        yield session
        await session.commit()
    except Exception as e:
        if session:
            await session.rollback()
        raise e
    finally:
        if session:
            await session.remove()
            await session.close()


from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

# Replace the placeholder with your Atlas connection string
# uri = "<connection string>"

# Set the Stable API version when creating a new client
mongo_client = AsyncIOMotorClient(settings.MONGO_URL, server_api=ServerApi('1'))


async def get_mongo_db(db_name: str) -> AsyncIOMotorClient:
    mongo_db = mongo_client[db_name]
    return mongo_db
