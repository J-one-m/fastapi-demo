# 注册 / 登录校验
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.resp import Resp
from db.session import get_db
from models import Gender, User
from schemas.common.schema_auth import RegisterReq, RegisterResp

"""
    待办：
        1. 日志记录后续补充
        2. 
"""
router = APIRouter(prefix="/auth", tags=["系统身份认证模块"])   #tags表示路由分类，方便文档展示，也可以在接口中单独使用

# 对于响应体类型的应用：通过response_model参数指定接收的响应体类型，或者通过函数返回类型注解，再或者两者都写
@router.post(   
    "/register",                          # 路径（必填，第一个参数）
    status_code=201,                      # 状态码（成功）
    summary="用户注册",                    # 文档摘要定义
    response_model=Resp[RegisterResp],    # 响应模型
    description="用户注册接口",            # 文档描述定义
)
async def register(req: RegisterReq, db: AsyncSession = Depends(get_db)):
    # 1.查重
    exists = await db.scalar(select(User).where(User.account_name == req.account_name))
    if exists:
        return Resp[RegisterResp].error(errcode=409, msg="账户名已存在")
    # 2.建对象
    user = User(
        account_name=req.account_name,
        account="",                         # 先占位，flush拿到id后再回填 
        gender=Gender(req.gender),
        age=req.age or 0,
        password=req.password,
    ) 
    # 3. 入库
    db.add(user)
    try:
        await db.flush()                    # 拿到自增id（尚未提交）
        user.account = f"{user.id:09d}" # 用id生成9位账号
        await db.commit()

    except Exception as e:
        await db.rollback()
        return Resp[RegisterResp].error(errcode=500, msg=f"注册失败：{e}")

    await db.refresh(user)
    return Resp[RegisterResp].success(data=RegisterResp.model_validate(user))