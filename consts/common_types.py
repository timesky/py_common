from enum import unique
from commons.cores.base_const import BaseEnum


@unique
class YesOrNo(BaseEnum):
    """通用类型，是或否"""

    YES = ('yes', '是')
    NO = ('no', '否')
