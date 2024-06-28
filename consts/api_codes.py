from enum import unique
from commons.cores.base_const import BaseEnum


@unique
class ApiCodes(BaseEnum):
    """接口返回码"""

    SUCCESS = ('success', '成功')
