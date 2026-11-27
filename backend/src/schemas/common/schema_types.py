import re
from typing import Annotated, Literal
from pydantic import AfterValidator

"""
re为Python 标准库的正则表达式模块
Annotated 为Python 标准库的类型注解模块
AfterValidator 为pydanticV2的 校验器模块，用于在字段校验后执行自定义校验逻辑

"""

def _check_password(v: str)-> str:
    allowed = r"^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]+$"
    if not re.match(allowed, v):
        raise ValueError("密码只能包含字母、数字和指定的特殊符号")
    if not re.search(r"[0-9]", v):
        raise ValueError("密码必须包含数字")
    if not re.search(r"[A-Z]", v):
        raise ValueError("密码必须包含大写字母")
    if not re.search(r"[a-z]", v):
        raise ValueError("密码必须包含小写字母")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", v):
        raise ValueError("密码必须包含特殊符号")

    return v
# 用 Annotated 把“类型 + 校验器”组合成一个新类型 Password，模型字段直接用这个类型。
# 本质是str类型，但附加了元数据AfterValidator，表明在校验后还需要再跑一遍_check_password，这是把校验规则“编码进类型”，类型即规则
Password = Annotated[str, AfterValidator(_check_password)]

# 性别取值范围与 models.user.Gender 保持一致；
# 用 Literal 让非法值在校验阶段返回 422，而不是走到 Gender(...) 抛 ValueError 变成 500
GenderLiteral = Literal["男", "女", "保密"]
