import contextvars

# 定义一个全局的上下文变量，用于存储额外信息
log_extra_unique_id = contextvars.ContextVar("log_extra_request_id", default=None)


class MaskUniqueID:
    """
    对log_extra_unique_id进行封装
    因为logger.configure()中的extra参数无法传递contextvars.ContextVar
    """

    def set(self, value):
        log_extra_unique_id.set(value)

    def __str__(self) -> str:
        # 在进行logger.configure时，此处可以动态返回log_extra_unique_id
        return str(log_extra_unique_id.get())


log_uid = MaskUniqueID()
log_uid.set('')

DEFAULT_LOG_FORMAT = (
    '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}.{function}:{line} | uid:{extra[unique_id]} | {message}'
)
