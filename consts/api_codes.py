from enum import unique
from commons.cores.base_const import BaseEnum


@unique
class ApiCodes(BaseEnum):
    """接口返回码"""

    SUCCESS = ('SUCCESS', '成功')
    UNKNOWN_ERROR = ('UNKNOWN_ERROR', '未知错误')
    SITE_ERROR = ('SITE_ERROR', '站点报错')
    NO_SEARCH_RESULT = ('NO_SEARCH_RESULT', '无搜索结果')
