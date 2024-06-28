from enum import unique
from commons.cores.base_const import BaseEnum


@unique
class FlightSiteType(BaseEnum):
    """机票资源站点类型"""

    AIRLINE = ('airline', '航空公司')
    OTA = ('ota', 'OTA平台')
