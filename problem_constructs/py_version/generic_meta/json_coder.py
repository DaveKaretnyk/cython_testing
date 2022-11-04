#  Copyright (c) 2022 by Thermo Fisher Scientific
#  All rights reserved. This file includes confidential and proprietary information
#  of Thermo Fisher Scientific
from enum import Enum
from typing import Callable, cast, Dict, Iterable, List, Set, Tuple, Type, Union

from .i_json_encodable import IJsonEncodable


class JsonCoder:
    """
    Encoder / decoder for simple types. Currently supports int, float, str and Enum.
    """
    _bool_prefix = "Bool::"  # const
    enum_prefix = "Enum::"  # const
    list_prefix = "List::"  # const
    _none_prefix = "NoneType::"  # const
    _number_prefix = "Number::"  # const
    _set_prefix = "Set::"  # const
    _tuple_prefix = "Tuple::"  # const

    SUPPORTED_TYPE = Union[Enum, bool, int, float, list, None, set, str, tuple, IJsonEncodable]

    @classmethod
    # pylint: disable=too-many-return-statements
    def encode(cls, item: "JsonCoder.SUPPORTED_TYPE") -> str:
        if isinstance(item, bool):
            return cls._bool_encode(item)
        if isinstance(item, Enum):
            return cls.enum_encode(item)
        if isinstance(item, (int, float)):
            return cls._number_encode(item)
        if isinstance(item, list):
            return cls._list_encode(item)
        if isinstance(item, type(None)):
            return cls._none_encode(item)
        if isinstance(item, set):
            return cls._set_encode(item)
        if isinstance(item, tuple):
            return cls._tuple_encode(item)
        if isinstance(item, str):
            return item
        if isinstance(item, IJsonEncodable):
            return item.json_encode()
        raise ValueError("{} is not supported by {}.encode".format(type(item), cls.__name__))

    @classmethod
    # pylint: disable=too-many-return-statements
    def decode(cls, string: str, type_dict: Dict[str, Type[Union[Enum, IJsonEncodable]]]) -> (
            "JsonCoder.SUPPORTED_TYPE"):  # noqa: F821
        if cls._is_bool(string):
            return cls._bool_decode(string)
        if cls._is_enum(string):
            return cls.enum_decode(string, type_dict)
        if cls._is_list(string):
            return JsonCoder._list_decode(string, type_dict)
        if cls._is_none(string):
            return cls._none_decode(string)
        if cls._is_number(string):
            return cls._number_decode(string)
        if cls._is_set(string):
            return JsonCoder._set_decode(string, type_dict)
        if cls._is_tuple(string):
            return JsonCoder._tuple_decode(string, type_dict)
        if "::" in string:
            data_type_name, _ = string.split("::", 1)
            data_type = type_dict.get(data_type_name, None)
            if data_type is not None:
                return cast(IJsonEncodable, data_type).json_decode(string, type_dict)
        return string

    @classmethod
    def _is_bool(cls, key: str) -> bool:
        return key.startswith(cls._bool_prefix)

    @classmethod
    def _bool_encode(cls, boolean) -> str:
        return cls._bool_prefix + str(boolean)

    @classmethod
    def _bool_decode(cls, key: str) -> bool:
        return cls._remove_prefix(key, cls._bool_prefix) == str(True)

    @classmethod
    def _is_enum(cls, key: str) -> bool:
        return key.startswith(cls.enum_prefix)

    @classmethod
    def enum_encode(cls, item: Enum) -> str:
        return f"{cls.enum_prefix}{item.__class__.__name__}.{item.name}"

    @classmethod
    def enum_decode(cls, key: str,
                    allowed_key_types: Dict[str, Type[Union[Enum, IJsonEncodable]]]) -> Enum:
        enum_type, name = cls._remove_prefix(key, cls.enum_prefix).split(".", maxsplit=1)
        enum = cast(Type[Enum], allowed_key_types[enum_type])
        return cast(Enum, enum[name])

    @classmethod
    def _is_list(cls, key: str) -> bool:
        return key.startswith(cls.list_prefix)

    @classmethod
    def _list_encode(cls, list_item: List["JsonCoder.SUPPORTED_TYPE"]) -> str:
        return "{}[{}]".format(cls.list_prefix, ", ".join(cls.encode(item) for item in list_item))

    @classmethod
    def _list_decode(cls, key: str,
                     allowed_key_types: Dict[str, Type[Union[Enum, IJsonEncodable]]]) -> (
            List["JsonCoder.SUPPORTED_TYPE"]):
        return cast(List[JsonCoder.SUPPORTED_TYPE],
                    cls._iterable_decode(key, allowed_key_types, cls.list_prefix, list))

    @classmethod
    def _is_none(cls, key: str) -> bool:
        return key.startswith(cls._none_prefix)

    @classmethod
    def _none_encode(cls, none: None) -> str:
        return cls._none_prefix + str(none)

    @classmethod
    def _none_decode(cls, _key: str) -> None:
        return None

    @classmethod
    def _is_number(cls, key: str) -> bool:
        return key.startswith(cls._number_prefix)

    @classmethod
    def _number_encode(cls, number: Union[int, float]) -> str:
        return cls._number_prefix + str(number)

    @classmethod
    def _number_decode(cls, key: str) -> Union[int, float]:
        number = float(cls._remove_prefix(key, cls._number_prefix))
        if number % 1 == 0.:
            return int(number)
        return number

    @classmethod
    def _is_set(cls, key: str) -> bool:
        return key.startswith(cls._set_prefix)

    @classmethod
    def _set_encode(cls, set_item: Set["JsonCoder.SUPPORTED_TYPE"]) -> str:
        return cls._set_prefix + "{" + ", ".join(cls.encode(item) for item in set_item) + "}"

    @classmethod
    def _set_decode(cls, key: str, allowed_key_types: Dict[str, Type[
            Union[Enum, IJsonEncodable]]]) -> Set["JsonCoder.SUPPORTED_TYPE"]:
        return cast(Set[JsonCoder.SUPPORTED_TYPE],
                    cls._iterable_decode(key, allowed_key_types, cls._set_prefix, set))

    @classmethod
    def _is_tuple(cls, key: str) -> bool:
        return key.startswith(cls._tuple_prefix)

    @classmethod
    def _tuple_encode(cls, tuple_item: Tuple["JsonCoder.SUPPORTED_TYPE", ...]) -> str:
        return "{}({})".format(cls._tuple_prefix,
                               ", ".join(cls.encode(item) for item in tuple_item))

    @classmethod
    def _tuple_decode(cls, key: str,
                      allowed_key_types: Dict[str, Type[Union[Enum, IJsonEncodable]]]) -> (
            Tuple["JsonCoder.SUPPORTED_TYPE", ...]):
        return cast(Tuple[JsonCoder.SUPPORTED_TYPE, ...],
                    cls._iterable_decode(key, allowed_key_types, cls._tuple_prefix, tuple))

    @classmethod
    def _iterable_decode(cls, key: str, allowed_key_types: Dict[str, Union[Type[Enum], Type[
            IJsonEncodable]]], prefix: str, create_iterable: Callable[..., Iterable]) -> (
            Iterable["JsonCoder.SUPPORTED_TYPE"]):
        key = cls._remove_prefix(key, prefix)
        key = key[1:-1]

        if not key:
            return create_iterable()

        return create_iterable(cls.decode(item, allowed_key_types)
                               for item in cls.split_commas_respect_parentheses(key))

    @classmethod
    def split_commas_respect_parentheses(cls, json_string: str) -> List[str]:
        items = json_string.split(", ")

        merged_items: List[str] = []
        balance_parentheses = 0
        balance_square_brackets = 0
        balance_curly_brackets = 0
        for item in items:
            if (balance_parentheses == 0 and balance_curly_brackets == 0
                    and balance_square_brackets == 0):
                merged_items.append(item)
            else:
                merged_items[-1] = "{}, {}".format(merged_items[-1], item)

            balance_parentheses += item.count("(") - item.count(")")
            balance_square_brackets += item.count("[") - item.count("]")
            balance_curly_brackets += item.count("{") - item.count("}")
        return merged_items

    @classmethod
    def _remove_prefix(cls, text: str, prefix: str) -> str:
        if text.startswith(prefix):
            return text[len(prefix):]
        return text
