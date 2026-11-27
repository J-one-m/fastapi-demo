# 注册 / 登录校验
from datetime import datetime

from fastapi import APIRouter, Request
from sqlalchemy import select

from core.deps import DbSession
from core.resp import Resp
from core.security import token_manager
from models import Gender, User
from schemas.auth.schema_auth import AuthResult, LoginReq, RegisterReq
from schemas.user.schema_user import UserInfo

"""
    待办：
        1. 日志记录后续补充
        2. 密码目前明文存储，后续替换为哈希校验
"""
router = APIRouter(prefix="/auth", tags=["认证"])


# 对于响应体类型的应用：通过response_model参数指定接收的响应体类型，或者通过函数返回类型注解，再或者两者都写
@router.post(
    "/register",                          # 路径（必填，第一个参数）
    # status_code=201,                    # 状态码（成功）国内后端一般不设置
    summary="用户注册",                    # 文档摘要定义
    response_model=Resp[AuthResult],      # 响应模型
    description="注册成功即自动登录，直接返回 token",   # 文档描述定义
)
# db 是形参名；DbSession 是它的类型注解，同时携带依赖声明（Depends(get_db)）；
# 实参是运行时由 get_db 产出并注入的 AsyncSession 实例
async def register(req: RegisterReq, db: DbSession):
    # 1.查重（此时还没有任何写入，返回错误响应是安全的）
    exists = await db.scalar(select(User).where(User.account_name == req.account_name))
    if exists:
        return Resp[AuthResult].error(errcode=409, msg="账户名已存在")

    # 2.建对象
    user = User(
        account_name=req.account_name,
        account="",                         # 先占位，flush 拿到 id 后再回填
        gender=Gender(req.gender),
        age=req.age,
        password=req.password,
    )

    # 3.入库：只 flush 不 commit，commit / rollback 统一由 get_db 负责
    db.add(user)                            # 将对象添加到会话中，等待 flush
    await db.flush()                        # 发出 INSERT，拿到自增 id（事务未提交）
    user.account = f"{user.id:09d}"         # 用 id 生成 9 位账号，随 commit 一起落库

    return Resp[AuthResult].success(
        data=AuthResult(
            token=token_manager.create_token(user.id),
            user=UserInfo.model_validate(user),
        )
    )


# 登录接口
@router.post(
    "/login",
    summary="用户登录",
    response_model=Resp[AuthResult],
    description="校验账户名与密码，成功后更新最后登录信息并返回 token",
)
async def login(req: LoginReq, db: DbSession, request: Request):
    user = await db.scalar(select(User).where(User.account_name == req.account_name))
    if user is None or user.password != req.password:
        # 此时还没有任何写入，return 错误响应不会被 get_db 误提交
        return Resp[AuthResult].error(errcode=401, msg="账户名或密码错误")

    # 只改属性、不 commit：get_db 结束时统一提交，会自动 flush 成 UPDATE
    user.last_login_time = datetime.now()
    user.last_login_address = request.client.host if request.client else None

    return Resp[AuthResult].success(
        data=AuthResult(
            token=token_manager.create_token(user.id),
            user=UserInfo.model_validate(user),
        )
    )


# 用户登出接口
@router.post(
    "/logout",
    summary="用户登出",
    response_model=Resp[AuthResult],
    description="清除当前登录用户的 token，使后续请求无法通过校验",
)
async def logout():

    return Resp.success(data="暂不做实现")