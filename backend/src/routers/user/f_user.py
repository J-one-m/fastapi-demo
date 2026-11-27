# 用户相关接口（需要登录）
from fastapi import APIRouter, Depends

from core.deps import CurrentUser, get_current_user
from core.resp import Resp
from schemas.user.schema_user import UserInfo

# 对于用户相关接口，都需要先登录，所以这里统一添加依赖项进行校验合法性
# 但是如果后续有”公开接口“，例如查看他人主页，这时候就需要单独拆router或者绕开了
router = APIRouter(prefix="/user", tags=["用户"], dependencies=[Depends(get_current_user)])


@router.get(
    "/me",
    summary="获取当前登录用户信息",
    response_model=Resp[UserInfo],
)
async def get_me(current_user: CurrentUser):
    # 当前用户由 token 解析得到，不需要再注入 db
    return Resp[UserInfo].success(data=UserInfo.model_validate(current_user))


# # 用户信息修改
# @router.patch('/update', summary="用户信息修改", response_model=Resp)
# async def  update_user_info(
#     current_user: CurrentUser,
#     user_info: UserInfo,
# ):


#     return Resp.success() 


# # 用户密码修改
# @router.put('/update_password', summary="用户密码修改", response_model=Resp)
# async def update_user_password(

# ):


#     return Resp.success()