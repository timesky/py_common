from enum import unique
from commons.cores.base_const import BaseEnum


@unique
class FlightResourceSiteType(BaseEnum):
    """机票资源站点类型"""

    AIRLINE = ('airline', '航空公司')
    OTA = ('ota', 'OTA平台')


@unique
class FlightResourceSiteStatus(BaseEnum):
    NORMAL = ('normal', '正常')
    NOT_NORMAL = ('not_normal', '不正常')
