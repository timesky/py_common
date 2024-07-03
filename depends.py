'''
这里存放fastapi的depends
'''

from typing_extensions import Annotated
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import status

from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.LOGIN_URL)


def get_real_client_ip(request: Request) -> str:
    """
    获取真实的客户端 IP 地址
    """
    # 获取原始客户端 IP 地址
    client_ip = request.client.host

    # 检查 X-Forwarded-For 头字段，以获取真实的客户端 IP 地址
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0].strip()

    return client_ip


async def get_current_admin_id(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id: str = payload.get("id")
        if admin_id is None:
            raise credentials_exception

    except jwt.InvalidTokenError:
        raise credentials_exception

    return admin_id
