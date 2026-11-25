import enum 

from datetime import datetime
from sqlalchemy import DateTime, String, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base


class Gender(str, enum.Enum):
    MALE = "男"
    FEMALE = "女"
    SECRET = "保密"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}
    """
       用户表：其中mapped_column注解用于定义数据库字段的属性：
       primary_key=True：主键
       unique=True：唯一索引
       default=datetime.now：默认值为当前时间
       onupdate=datetime.now：更新时自动更新为当前时间
       comment="用户ID"：注释
       index=True：创建索引，用于快速查询用户名
       nullable=False/True：是否允许为空，默认False
       外键： 用foreign_key参数指定外键，例如：foreign_key="system_accounts.id"，表示外键指向system_accounts表的id字段
       default=：Python 层 默认值，插入时由 SQLAlchemy 填；只在 ORM 插入生效
       server_default=：数据库层 默认值，插入时由数据库填；在 ORM 插入生效


    补充，对于设置了unique=True的字段，数据库会自动创建唯一索引，此时不需要在显示的指定index=True，也包括primary_key=True的字段


    """
    id: Mapped[int] = mapped_column(primary_key=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(20), unique=True, comment="用户名")
    gender: Mapped[Gender] = mapped_column(
        SAEnum(
            Gender,
            name="gender_enum",
            native_enum=False,       # 关键：不用 MySQL 原生 ENUM，生成 VARCHAR + CHECK
            length=10,
            values_callable=lambda e: [m.value for m in e],  # 存“男”而不是“MALE”
        ),
        default=Gender.SECRET, 
        server_default=Gender.SECRET.value,
        comment="性别"
    )
    age: Mapped[int] = mapped_column(default=0, comment="年龄")
    password: Mapped[str] = mapped_column(String(20), comment="密码")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=datetime.now, comment="更新时间")








