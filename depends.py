'''
这里存放fastapi的depends
'''

from fastapi import Request


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
