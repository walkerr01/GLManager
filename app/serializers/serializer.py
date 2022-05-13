import enum
import datetime

from typing import TypeVar, Type, Any, Union
from json import JSONEncoder


def _parser_to_dict(obj: Any) -> Any:
    '''
    Converts object to dictionary.
    '''
    if isinstance(obj, dict):
        return {k: _parser_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_parser_to_dict(v) for v in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.utcnow()
    elif isinstance(obj, enum.Enum):
        return obj.value
    elif isinstance(obj, Serializer):
        return obj.to_dict()
    else:
        return obj


def _parser_to_json(obj: Any) -> Any:
    '''
    Converts object to JSON.
    '''
    return JSONEncoder(indent=4).encode(_parser_to_dict(obj))


class BaseSerializer:
    def to_dict(self) -> dict:
        return _parser_to_dict(self.__dict__)

    def to_json(self) -> str:
        return _parser_to_json(self.to_dict())


T = TypeVar('T', bound='Serializer')


class Serializer(BaseSerializer):
    def __init__(self: T, **kwargs: dict):
        self.update(kwargs)

    @classmethod
    def of(cls: Type[T], data: Union[dict, 'Serializer']) -> T:
        if isinstance(data, dict):
            return cls(**data)
        elif isinstance(data, Serializer):
            return cls(**data.to_dict())
        else:
            raise TypeError('Invalid data type')

    def update(self, data: Union[dict, 'Serializer']) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        elif isinstance(data, Serializer):
            self.update(data.to_dict())
        else:
            raise TypeError('Invalid data type')

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        if hasattr(self, key):
            setattr(self, key, value)