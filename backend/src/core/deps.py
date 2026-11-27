"""
数据库会话依赖项 + 登录鉴权依赖项

事务边界只在本文件内控制，路由和业务函数都不写 commit / rollback：
    - 请求正常结束 → 这里统一 commit
    - 请求抛出异常 → 这里统一 rollback，然后原样抛出

注意：依赖判断成功与失败，只看"有没有抛出异常"，不看返回值内容。
如果路由用 `return Resp.error(...)` 代替 `raise`，依赖会认为请求成功，
并把本次请求中已经 flush 的写入提交掉。所以业务失败必须 raise。
"""
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import TokenError, token_manager
from db.session import AsyncSessionLocal
from models import User


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


# ---------- 鉴权 ----------
# auto_error=False：没带 token 时不抛 403，而是返回 None，
# 这样 401 的状态码、文案和响应头都由自己控制
bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    """统一的 401 响应：对外不区分 未带 token / 过期 / 签名错 / 用户不存在"""
    return HTTPException(
        status_code=401,
        detail="登录凭证无效，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    """将请求头 Authorization: Bearer <token> 解析为当前用户"""
    if credentials is None:
        raise _unauthorized()

    try:
        # parse_user_id 内部完成验签、过期检查，并把 sub 转成 int
        user_id = token_manager.parse_user_id(credentials.credentials)
    except TokenError as exc:
        # exc.code / exc.detail 只写日志，不返回给客户端
        # logger.info("token 校验失败: %s | %s", exc.code, exc.detail)
        raise _unauthorized() from exc

    user = await db.get(User, user_id)
    if user is None:
        # 用户被删除，但 token 还没过期
        raise _unauthorized()

    return user


# 需要登录的接口直接声明 current_user: CurrentUser
CurrentUser = Annotated[User, Depends(get_current_user)]
