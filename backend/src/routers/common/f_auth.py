# 注册 / 登录校验
from core.resp import Resp
from schemas.common.schema_auth import RegisterReq, RegisterResp
from fastapi import APIRouter




"""
    待办：
        1. 日志记录后续补充
        2. 
"""
router = APIRouter(prefix="/auth", tags=["系统身份认证模块"])

@router.post("/register", summary="用户注册", response_model=Resp[RegisterResp])
async def register(req: RegisterReq):

    try:

        return Resp[RegisterResp].success(data=RegisterResp.model_validate({
            "id": 1,
            "account_name": req.account_name,
            "account": '220591021',
            "gender": req.gender,
            "age": req.age,
            "last_login_time": datetime.now(),
            "last_login_address": "127.0.0.1",
        }))

    except Exception as e:
        return Resp.error(msg=str(e), code=400)



