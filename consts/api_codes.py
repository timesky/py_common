from enum import unique
from commons.cores.base_const import BaseEnum


@unique
class ApiCodes(BaseEnum):
    """接口返回码"""

    SUCCESS = ('SUCCESS', '成功')
    UNKNOWN = ('UNKNOWN', '未知错误')
    SITE_ERROR = ('SITE_ERROR', '站点报错')
    NO_SEARCH_RESULT = ('NO_SEARCH_RESULT', '无搜索结果')
    SEARCH_TIMEOUT = ('SEARCH_TIMEOUT', '限定时间内无搜索结果')
    NO_ACCOUNT = ('NO_ACCOUNT', '无可用账号')
    NO_FOUND = ('NO_FOUND', '记录未找到')
    LOCK_ERROR = ('LOCK_ERROR', '已被锁定')
