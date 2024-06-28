from typing import Optional
from pydantic import BaseModel


class BaseApiRequestModel(BaseModel):
    request_id: Optional[str] = None
    params: Optional[BaseModel] = None
