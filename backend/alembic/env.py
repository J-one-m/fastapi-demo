"""
数据库迁移脚本
- 用于生成和应用数据库迁移脚本
- 依赖 Alembic 配置文件（会执行每条Alembic中的每条命令，职责是三件事：读配置、拿到模型元数据、提供数据库连接。
其中target_metadata决定“拿什么和数据库对比”）
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# 导入项目配置和模型基类
from config import settings
from app.base import Base
import models # 导入模型才会注册到Base.metadata中

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate 依靠它对比模型与数据库
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：只生成 SQL 脚本，不连数据库"""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """供 online 模式调用的同步迁移函数"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """在线模式：真正连接数据库执行迁移"""
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())