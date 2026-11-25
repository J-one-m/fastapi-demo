from sqlalchemy.orm import DeclarativeBase

# 定义sqlalchemy的声明式基类，所有模型都将继承它。它是orm映射的核心
"""
为什么需要?:
- 将Base单独放在一个文件中，便于其它模型文件导入，也方便alembic的env.py文件导入（from app.models import Base）
- 避免循环导入：如果Base定义在user.py中，其它模型导入时可能出现依赖混乱。
"""
class Base(DeclarativeBase):
    pass

