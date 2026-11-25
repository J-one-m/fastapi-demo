import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from config import settings
from app.base import Base
from routers import system_account


# 创建app应用
app = FastAPI()


app.include_router(system_account.router, prefix="/api/v1")# 定义路由前缀，这里表示所有路由都以/api/v1开头





# 通过
if __name__ == "__main__":      #表示只有该文件被直接运行时才执行下面的代码，被别的文件通过import的方式导入时不执行
    uvicorn.run(
        "src.main:app",        #告诉uvicon去哪找FastAPI实例，main对应main.py，app对应文件里的app变量
        host="127.0.0.1",       #需要监听的网卡，当前值表示本机地址
        port=8000,              #定义端口号
        reload=True,            #是否启用热重载（即保存更改自动重启服务）
    )