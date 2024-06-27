from abc import ABC, abstractmethod


class BaseFlightServices(ABC):
    @property
    @abstractmethod
    def airline_name(self):
        raise AttributeError

    @abstractmethod
    def search(self, dep: str, arr: str, dep_date: str, return_date: str, adult=1):
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name in dir(cls):
            if name.startswith('__'):
                continue
            attr = getattr(cls, name)
            if callable(attr) and not hasattr(BaseFlightServices, name):
                raise TypeError(f"不能在 {cls.__name__} 声明 '{name}' 方法。 只能声明父类定义的方法。")
