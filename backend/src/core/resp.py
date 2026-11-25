# 定义系统接口响应类型
"""
返回结构示例：
{
    "errcode": 0,       #业务状态码
    "msg":"",           #提示信息
    "data": any_data,   #业务处理结果
}
"""
from pydantic import BaseModel, Field


class Resp[T](BaseModel):
    errcode: int = Field(default=0, description='业务状态码，0表示成功')
    msg: str = Field(default='success', description='提示信息')
    data: T | None = Field(default=None, description='业务处理结果')

    # 定义响应体类方法，其中cls指的是类本身
    @classmethod
    def success(cls, data: T | None = None, msg: str = "success") -> Resp[T]:
        return cls(errcode=0, msg=msg, data=data)


    @classmethod
    def error(cls, errcode: int = 400, msg: str = "error") -> Resp[T]:
        #如果错误信息为空，手动注入错误信息
        if msg is None:
            msg = "定义错误信息"

        return cls(errcode=errcode, msg=msg, data=None)
