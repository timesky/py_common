from typing import Optional, Union
from pydantic import BaseModel


class BaseApiRequestModel(BaseModel):
    request_id: Optional[str] = None
    params: Optional[BaseModel] = None


class BaseApiResponseModel(BaseModel):
    code: Union[int, str]
    message: str
    data: Optional[BaseModel] = None
    client_ip: str
    request_id: str
