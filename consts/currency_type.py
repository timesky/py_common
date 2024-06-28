from enum import unique
from app.commons.cores.base_const import BaseEnum


@unique
class CurrencyType(BaseEnum):
    """币种"""

    CNY = ('CNY', '人民币')
    USD = ('USD', '美元')
    EUR = ('EUR', '欧元')
