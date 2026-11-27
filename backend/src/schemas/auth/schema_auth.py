# 注册 / 登录校验
from pydantic import BaseModel, Field

from schemas.common.schema_types import GenderLiteral, Password
from schemas.user.schema_user import UserInfo


# ========== 注册 ==========
class RegisterReq(BaseModel):
    account_name: str = Field(..., min_length=2, max_length=20, description="账户名")
    gender: GenderLiteral = Field(default="保密", description="性别")
    password: Password = Field(..., min_length=6, max_length=18, description="密码")
    age: int = Field(default=0, ge=0, le=150, description="年龄")


# ========== 登录 ==========
class LoginReq(BaseModel):
    account_name: str = Field(..., min_length=2, max_length=20, description="账户名")
    # 登录不复用 Password 的复杂度规则：规则一旦收紧，老用户会被挡在门外，
    # 而且 422 的报错信息会泄露密码格式要求
    password: str = Field(..., min_length=1, max_length=18, description="密码")


# ========== 响应 ==========
class AuthResult(BaseModel):
    """鉴权结果：注册、登录共用（按视图组合，不按接口复制字段）"""

    token: str = Field(..., description="访问令牌，请求头用 Authorization: Bearer <token>")
    user: UserInfo = Field(..., description="用户信息")
