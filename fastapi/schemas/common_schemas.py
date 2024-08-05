# 基础模块
from typing import Optional
from pydantic import BaseModel


class BaseSearchOrderBy(BaseModel):
    prop: str = None
    order: str = None


class BaseSearchRequest(BaseModel):
    page: int = 1
    page_size: int = 50
    order_by: Optional[BaseModel] = None


class BaseResponse(BaseModel):
    code: str
    message: str
    data: Optional[BaseModel] = None
    client_ip: str
    request_id: str
