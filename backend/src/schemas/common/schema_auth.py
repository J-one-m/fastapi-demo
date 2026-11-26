# 注册 / 登录校验
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from .schema_types import Password


# ========== 注册 ==========
"""
    token、密码加密这些后续再说
"""
# 注册请求模型
class RegisterReq(BaseModel):
    account_name: str = Field(..., max_length=18, min_length=2, description="账号名称")
    gender: str = Field(description="性别", default="保密")
    password: Password = Field(..., min_length=6, max_length=18, description="密码")
    age: int | None = Field(default=0, ge=0, le=150, description="年龄")


# 注册响应模型
class RegisterResp(BaseModel):
    model_config = ConfigDict(from_attributes=True)                                 # 允许从 ORM 对象构造（？）

    id: int = Field(..., description="用户ID")
    account_name: str = Field(..., description="账号名称") #不可设置默认值，否则字段会变为可选
    account: str = Field(..., min_length=9, max_length=9, description="账号")
    gender: str = Field(description="性别")
    age: int = Field(description="年龄")
    last_login_time: datetime | None = Field(default=None, description="上次登录时间")
    last_login_address: str | None = Field(default=None, description="上次登录地址")
