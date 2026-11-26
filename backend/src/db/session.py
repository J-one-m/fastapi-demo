# 数据库会话管理：只负责创建连接池和会话工厂
# FastAPI 的会话依赖（get_db / DbSession）在 core/deps.py 中定义
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings

# 全局唯一的引擎（内含连接池），整个应用生命周期只创建一次
engine = create_async_engine(
    settings.DATABASE_URL,  # .env / 环境变量里的连接串，决定连 MySQL 还是 SQLite
    pool_pre_ping=True,     # 取连接前先探活，防止 MySQL 空闲超时后拿到死连接
    echo=settings.DEBUG,    # DEBUG=True 时打印所有 SQL，调试用
)

# 会话工厂：不直接产生会话，而是"每次调用产生一个新会话"
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,    # 显式指定异步会话类
    expire_on_commit=False, # commit 后对象不过期，提交后仍能读取属性
    autoflush=False,        # 不自动 flush，SQL 什么时候发可预期
)