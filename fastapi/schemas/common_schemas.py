# 基础模块
from typing import Any, List, Optional, Union
from pydantic import BaseModel


class BaseSearchOrderBy(BaseModel):
    prop: str = None
    order: str = None


class BaseSearchIn(BaseModel):
    page: int = 1
    page_size: int = 50
    order_by: Optional[BaseModel] = None


class BaseSearchResult(BaseModel):
    '''查询出参data'''

    total: int
    # page: int
    rows: List[BaseModel]


class BaseApiOut(BaseModel):
    code: str
    message: Optional[str] = None
    data: Optional[Any] = None
    client_ip: Optional[str] = None
    request_id: Optional[str] = None
