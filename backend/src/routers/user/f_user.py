# 用户相关接口
from core.resp import Resp
from fastapi import APIRouter, Depends



routers = APIRouter(prefix="/user", tags=["用户模块"])

@router.get('/get_user', summary="获取当前用户登录信息", response_model=Resp)
def get_user():

    return Resp.success()





