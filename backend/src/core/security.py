"""鉴权相关工具

本模块只做两件事：
    - 签发 token：create_token
    - 校验 token 并取出用户 ID：parse_user_id

不查数据库、不碰 HTTP：会话获取与 401 响应都在 core/deps.py 里完成，
这样本文件可以脱离 FastAPI 单独测试。
"""
import time
from datetime import timedelta
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from config import settings


class TokenError(Exception):
    """token 无效

    code 只给程序判断（TOKEN_EXPIRED / TOKEN_INVALID），
    detail 保留真实原因，只写日志，不要返回给客户端。
    """

    def __init__(self, code: str = "TOKEN_INVALID", detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(detail or code)


# token签发与认证
class TokenManager:
    """token的签发与校验（PyJWT 封装）

    实例仅保存配置、不保存请求状态，可被所有请求共享。
    """

    # token管理类初始化，传入三个参数，分别是密钥、过期时间、算法类型
    def __init__(self, secret_key: str, expires_minutes: int, algorithm: str = "HS256"):
        if algorithm not in {"HS256", "HS384", "HS512"}:
            raise ValueError("仅支持 HMAC 系列算法")
        # HS256 的安全性完全取决于密钥熵；生产环境请用 32 位以上的随机值
        if len(secret_key) < 16:
            raise ValueError("SECRET_KEY 过短，至少 16 位")
        if expires_minutes <= 0:
            raise ValueError("expires_minutes 必须为正数")

        self._secret_key = secret_key
        self._expires_minutes = expires_minutes
        self._algorithm = algorithm

    # 签发token
    def create_token(self, user_id: int, expires_minutes: int | None = None) -> str:
        # 用 is None 判断而不是 or：传 0 / 负数时 or 会错误地回退到默认值
        minutes = self._expires_minutes if expires_minutes is None else expires_minutes
        now = int(time.time())
        payload = {
            "sub": str(user_id),   # RFC 7519 要求 sub 是字符串，PyJWT 2.10+ 会强校验
            "iat": now,
            "exp": now + minutes * 60,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    # 对于token的校验
    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],          # 必须显式给白名单，防 alg 混淆攻击
                options={"require": ["exp", "sub"]},   # 缺少 exp / sub 直接判无效
                leeway=timedelta(seconds=10),          # 容忍客户端与服务器的时间偏差
            )
        except ExpiredSignatureError as exc:
            raise TokenError("TOKEN_EXPIRED", str(exc)) from exc
        except InvalidTokenError as exc:
            # InvalidTokenError 是 PyJWT 所有解码异常的基类：
            # 格式错、签名错、算法不支持、JSON 不合法、aud/iss 不匹配等都在这里
            raise TokenError("TOKEN_INVALID", str(exc)) from exc

    # 从token解析user_id
    def parse_user_id(self, token: str) -> int:
        """verify 之后将 sub 转成 int，集中处理 KeyError / TypeError / ValueError"""
        payload = self.verify_token(token)
        try:
            user_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError) as exc:
            # 正常情况下 require=["sub"] 已保证存在，这里是防御性兜底：
            # sub 可能是 "abc" / "1.5" / null，int() 会失败
            raise TokenError("TOKEN_INVALID", "sub 不是合法用户 ID") from exc

        if user_id <= 0:
            raise TokenError("TOKEN_INVALID", "sub 不是合法用户 ID")
        return user_id


# 内部全局唯一实例：模块加载时创建一次，后续import时直接使用
token_manager = TokenManager(
    settings.SECRET_KEY,
    settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    # 算法写死，不从环境变量读，避免配置错误引入 none / RS 系列
    "HS256",
)
