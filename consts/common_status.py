from enum import unique
from commons.cores.base_const import BaseEnum


@unique
class EnableStatus(BaseEnum):
    """是否启用"""

    ENABLED = ('enabled', '启用')
    DISABLED = ('disabled', '禁用')
