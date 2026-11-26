"""
数据库会话依赖项

事务边界只在本文件内控制，路由和业务函数都不写 commit / rollback：
    - 请求正常结束 → 这里统一 commit
    - 请求抛出异常 → 这里统一 rollback，然后原样抛出

注意：依赖判断成功与失败，只看"有没有抛出异常"，不看返回值内容。
如果路由用 `return Resp.error(...)` 代替 `raise`，依赖会认为请求成功，
并把本次请求中已经 flush 的写入提交掉。所以业务失败必须 raise。
"""
from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import AsyncSessionLocal


async def get_db() -> AsyncIterator[AsyncSession]:
    """每个请求创建一个会话，请求结束自动提交或回滚

    yield 之前的代码在请求进入时执行，yield 之后的代码在请求结束时执行，
    async with 负责在最后关闭会话（close），无需手动调用。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session               # 把会话交给接口使用
            await session.commit()      # 正常返回：统一提交本次事务
        except Exception:
            await session.rollback()    # 出现异常：回滚本次事务
            raise                       # 用 raise 而不是 raise e，保留原始堆栈


# 路由中直接声明 db: DbSession 即可，类型和依赖合二为一
DbSession = Annotated[AsyncSession, Depends(get_db)]
