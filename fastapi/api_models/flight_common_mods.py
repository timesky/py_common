from typing import Dict, List, Optional
from pydantic import BaseModel


class Cabin(BaseModel):
    cabin_code: str  # 舱位代码
    count: int  # 舱位数量
    site_adt_price: float  # 站点价格
    site_adt_cny_price: Optional[float] = None  # 站点人民币价格
    real_time_adt_cny_price: Optional[float] = None  # 实时人民币价格


class Segment(BaseModel):
    segment_index: int  # 航段序号
    airline_code: str  # 航班号
    flight_number: str  # 航班序号
    dep_code: str  # 出发机场三字码
    arr_code: str  # 到达机场三字码
    dep_time: str  # 出发时间
    arr_time: str  # 到达时间


class FlightInfo(BaseModel):
    dep_code: str  # 出发机场三字码
    dep_name: str  # 出发机场名称
    arr_code: str  # 到达机场三字码
    arr_name: str  # 到达机场名称
    dep_date: str  # 出发日期
    site_code: str  # 站点
    flight_no: str  # 航班号
    site_lowest_price: float  # 站点最低价格
    site_currency_code: str  # 站点币种
    site_exchange_rate: Optional[float] = None  # 站点汇率
    site_lowest_cny_price: Optional[float] = None  # 站点最低人民币价格
    real_time_exchange_rate: Optional[float] = None  # 实时汇率
    real_time_lowest_cny_price: Optional[float] = None  # 实时最低人民币价格
    update_time: str
    cabins: Dict[str, Cabin]
    segments: List[Segment]
    stops: int
    dep_time: str
    arr_time: str
    supplier: Optional[str] = ""
    supplier_iata_id: Optional[str] = ""
