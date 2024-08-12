from enum import unique
from commons.cores.base_const import BaseEnum


@unique
class EnableStatus(BaseEnum):
    """是否启用"""

    ENABLED = ('enabled', '启用')
    DISABLED = ('disabled', '禁用')


@unique
class SuccessStatus(BaseEnum):
    SUCCESS = ('success', '成功')
    FAILED = ('failed', '失败')
