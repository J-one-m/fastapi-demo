from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_db
from config import settings
from pydantic import BaseModel, Field

router = APIRouter(prefix="/system_account", tags=["system_account"])


@router.get("/")
async def get_system_info():
    return { "system_info": {
        "app_name": settings.APP_NAME,
        "debug": settings.DEBUG,
    } }


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db": result.scalar()}


class CreateUserReq(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=8, max_length=20, description="密码")

# 后续可以利用Pydantic中的create_model方法来实现类似于ts中Pick / Omit的功能
class CreateUserResp(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    system_account: str = Field(..., min_length=9, max_length=9, description="系统账号")

# 对于响应体类型的应用：通过response_model参数接收响应体类型，或者通过函数返回类型注解，再或者两者都写
@router.post(
    '/create',                #路径（必填，第一个位置参数）
    response_model=CreateUserResp,                # 响应模型
    status_code=201,                              # 状态码
    summary= "文档摘要定义",
    description="文档描述：根据用户名密码创建系统账号",
    tags=["文档分组：system_account"],
)
async def create_user(req: CreateUserReq) -> CreateUserResp:
    return CreateUserResp(
        username=req.username,
        system_account='220591021',
    )