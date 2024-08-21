'''
这里存放fastapi的depends
'''

from typing import Optional
from typing_extensions import Annotated
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import status
from loguru import logger


def get_real_client_ip(request: Request) -> str:
    """
    获取真实的客户端 IP 地址。
    如果有 X-Forwarded-For 头字段，使用其中的第一个 IP 地址作为真实客户端 IP。
    否则使用 request.client.host 获取的 IP。
    """
    # 获取 X-Forwarded-For 头字段的值
    x_forwarded_for = request.headers.get("X-Forwarded-For")

    if x_forwarded_for:
        # 返回第一个 IP 地址（即最原始的客户端 IP）
        return x_forwarded_for.split(',')[0].strip()

    # 否则返回原始客户端 IP
    return request.client.host


async def get_current_user_id(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="token"))],
    secret_key: str,
    algorithm: str,
    user_id_field: str = "id",
) -> Optional[str]:
    """
    获取当前用户 ID 的通用方法，使用 JWT 令牌验证。

    :param token: 传递的 JWT 令牌
    :param secret_key: 用于解密 JWT 的密钥
    :param algorithm: 用于解密 JWT 的算法
    :param user_id_field: JWT 载荷中的用户 ID 字段名
    :return: 用户 ID（如果验证成功），否则返回 None
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 解码 JWT 令牌
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        # logger.debug(payload)
        user_id: Optional[str] = payload.get(user_id_field)
        # logger.debug(user_id)

        # 如果没有用户 ID，抛出验证异常
        if user_id is None:
            raise credentials_exception

    except jwt.PyJWTError:  # 捕获所有 JWT 相关的错误
        raise credentials_exception

    return user_id
