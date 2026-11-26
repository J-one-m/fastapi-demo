# 注册 / 登录校验
from fastapi import APIRouter
from sqlalchemy import select

from core.deps import DbSession
from core.resp import Resp
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
    # status_code=201,                      # 状态码（成功）国内后端一般不设置
    summary="用户注册",                    # 文档摘要定义
    response_model=Resp[RegisterResp],    # 响应模型
    description="用户注册接口",            # 文档描述定义
)
# db 是形参名；DbSession 是它的类型注解，同时携带依赖声明（Depends(get_db)）；
# 实参是运行时由 get_db 产出并注入的 AsyncSession 实例
async def register(req: RegisterReq, db: DbSession):
    # 1.查重（此时还没有任何写入，返回错误响应是安全的）
    exists = await db.scalar(select(User).where(User.account_name == req.account_name))
    if exists:
        return Resp[RegisterResp].error(errcode=409, msg="账户名已存在")

    # 2.建对象
    user = User(
        account_name=req.account_name,
        account="",                         # 先占位，flush 拿到 id 后再回填
        gender=Gender(req.gender),
        age=req.age or 0,
        password=req.password,
    )

    # 3.入库：只 flush 不 commit，commit / rollback 统一由 get_db 负责
    db.add(user)
    await db.flush()                        # 发出 INSERT，拿到自增 id（事务未提交）
    await db.refresh(user)                  # 读回数据库生成的 create_time
    user.account = f"{user.id:09d}"         # 用 id 生成 9 位账号，随 commit 一起落库

    return Resp[RegisterResp].success(data=RegisterResp.model_validate(user))