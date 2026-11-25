# 注册 / 登录校验
from datetime import datetime

from pydantic import BaseModel, Field



# ========== 注册 ==========
"""
    token、密码加密这些后续再说
"""
# 注册响应模型
class RegisterResp(BaseModel):
    id: int = Field(..., description="用户ID")
    account_name: str = Field(default="南风", description="账号名称")
    account: str = Field(..., min_length=9, max_length=9, description="账号")
    gender: str = Field(description="性别")
    age: int = Field(description="年龄")
    last_login_time: datetime = Field(..., description="上次登录时间")
    last_login_address: str = Field(..., description="上次登录地址")

# 注册请求模型
class RegisterReq(BaseModel):
    account_name: str = Field(..., max_length=18, min_length=2, description="账号名称")
    gender: str = Field(description="性别", default="保密")
    age: int | None = Field(default=None, description="年龄")