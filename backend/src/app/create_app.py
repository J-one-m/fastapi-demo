# create_app.py用于创建FastAPI应用（可以带lifespan、全局中间件、/static挂载）
from fastapi import FastAPI

from core.register import register_all

def create_app()-> FastAPI:
    # 可传入参数
    _app = FastAPI()
    register_all(_app) # 对于在内部注册还是外部注册，后续再考虑

    return _app

app  = create_app()
