"""
项目全局配置：
作用是管理所有配置项（数据库URL、密钥等），从.env文件中读取，便于在不同环境（开发/测试/生产）中切换

在项目中的作用：
- Alembic 的 env.py 通过 from app.core.config import settings 获取数据库 URL，实现动态配置，无需硬编码在 alembic.ini 中。
- FastAPI 应用也可以用它读取其他配置（如 SECRET_KEY、DEBUG 模式）。
"""
# BaseSettings是 Pydantic的配置基类，能自动从环境变量或.env文件读取，并进行类型校验
import sys
from typing import Final

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# 定位.env文件位置
"""
    __file__：当前模块的文件路径
    resolve()：将路径解析为绝对路径
    parent.parent：获取当前模块的父目录的父目录（项目根目录）
    / ".env"：在项目根目录下查找 .env 文件
"""
ROOT_DIR: Final[Path] = Path(__file__).resolve().parent.parent
ENV_PATH: Final[Path] = ROOT_DIR / ".env"

# ENV_PATH是一个Path对象，其中exists方法是其独有的
if not ENV_PATH.exists():
    msg = f"环境变量文件{ENV_PATH}不存在"
    print(msg)
    # 退出程序，返回非0状态码，表示程序异常退出
    sys.exit(1)
    


# 定义配置类

# 定义系统配置类
class ServerSettings(BaseSettings):
    """默认后端服务器系统配置类"""
    """
    model_config定义了配置行为
        - env_file=".env"：指定读取项目根目录下的.env文件
        - env_file_encoding="utf-8"：文件编码。
        - extra="ignore"：忽略 .env 中未在类中定义的变量，防止报错。
        
    APP_NAME、DEBUG、DATABASE_URL 是配置字段，带有默认值。
    如果 .env 中有对应的键（如 DATABASE_URL），则会覆盖默认值。
    """
    model_config = SettingsConfigDict(
        # 对于Pydantic V2，同时支持Path和str，所以不需要使用str进行转换，但是如果为了兼容V1，则需要使用str()进行转换
        env_file=str(ENV_PATH), 
        env_file_encoding="utf-8", 
        extra="ignore",
    )

    APP_NAME: str = "FastAPI Project"
    DEBUG: bool = False
    #学习或者demo（单机小工具：爬虫数据、笔记、桌面应用这些）推荐使用SQLite，后续可在换成MySQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db" #其中的aiosqlite是驱动名，固定三个斜杠表示相对路径，app.db是数据库文件名
    # 如果需要将本地数据库换成线上的服务器，可以将@符后的本机地址替换为线上服务器的地址
    # DATABASE_URL: str = "mysql+aiomysql://root:123456%40fgj@localhost:3306/learn_test?charset=utf8mb4" #MySQL数据库连接字符串
# settings = ServerSettings() 在模块加载时立即实例化，后续通过
# from app.core.config import settings 获取配置对象。
settings = ServerSettings()




