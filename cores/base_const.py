from enum import Enum, unique


@unique
class BaseEnum(Enum):
    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj

    @classmethod
    def keys(cls):
        return [member.value for member in cls]

    @classmethod
    def values(cls):
        return [member.label for member in cls]

    @classmethod
    def mappings(cls):
        return {member.value: member.label for member in cls}

    def raise_error(self, ext_msg: str = None) -> Exception:
        code = self._value_
        msg = self.label
        if ext_msg:
            msg = f'{msg}: {ext_msg}'
        raise Exception(code, msg)

    def generate_api_result(
        self, ext_msg: str = None, data: dict = None, client_ip: str = '', request_id: str = ''
    ) -> dict:
        code = self._value_
        msg = self.label
        if ext_msg:
            msg = f'{msg}: {ext_msg}'

        result = {'code': code, 'message': msg, 'client_ip': client_ip, 'request_id': request_id}
        if data:
            result['data'] = data
        return result
