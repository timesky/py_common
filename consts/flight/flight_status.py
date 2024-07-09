from enum import unique
from commons.cores.base_const import BaseEnum


@unique
class FlightFetchTaskStatus(BaseEnum):
    """搜索任务状态"""

    PENDING = ('pending', '等待中')
    RUNNING = ('running', '运行中')
    SUCCESS = ('success', '成功')
    FAILED = ('failed', '失败')
