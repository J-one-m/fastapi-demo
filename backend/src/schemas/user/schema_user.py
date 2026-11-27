from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserInfo(BaseModel):
    """用户信息视图：注册、登录、/me 三处共用"""

    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 对象属性构造

    id: int = Field(..., description="用户ID")
    account: str = Field(..., min_length=9, max_length=9, description="账号")
    account_name: str = Field(..., min_length=2, max_length=20, description="账户名")
    gender: str = Field(..., description="性别")
    age: int = Field(..., ge=0, le=150, description="年龄")
    last_login_time: datetime | None = Field(default=None, description="上次登录时间")
    last_login_address: str | None = Field(default=None, description="上次登录地址")
