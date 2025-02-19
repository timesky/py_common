from abc import ABC, abstractmethod, abstractproperty

from loguru import logger


class BaseFlightServices(ABC):

    @abstractmethod
    async def refresh_authorization(self):
        """授权信息刷新

        包括取账号，刷新cookies，token等
        """
        raise NotImplementedError

    @abstractmethod
    async def update_cities(self):
        """更新城市信息

        向站点独有的数据集中更新城市信息
        """
        raise NotImplementedError

    @abstractmethod
    async def search(self, dep_code: str, arr_code: str, dep_date: str, return_date: str, adult=1):
        """报价查询"""
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        required_attrs = ['SITE_CODE', 'AIRLINE_CODE', 'AIRLINE_NAME']
        sub_class_attrs = [name for name in dir(cls) if not name.startswith('__')]
        for name in sub_class_attrs:
            # if name.startswith('__') :
            #     continue
            logger.debug(name)
            attr = getattr(cls, name)
            if callable(attr) and not hasattr(BaseFlightServices, name):
                raise TypeError(f"不能在 {cls.__name__} 声明 '{name}' 方法。 只能声明父类定义的方法。")

        un_defined_attrs = [attr for attr in required_attrs if attr not in sub_class_attrs]
        if un_defined_attrs:
            raise TypeError(f"类 {cls.__name__} 缺少 {un_defined_attrs} 属性")
