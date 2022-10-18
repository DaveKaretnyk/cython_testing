#  Copyright (c) 2020 by Thermo Fisher Scientific
#  All rights reserved. This file includes confidential and proprietary information
#  of Thermo Fisher Scientific
from enum import Enum
from typing import Dict, Iterable, Type, Union

from .i_json_encodable import IJsonEncodable
from .json_coder import JsonCoder


class JsonEncodable(IJsonEncodable):

    @classmethod
    def default_type_mapping(cls, key_types: Iterable[Union[Type[Enum], Type[
            "IJsonEncodable"]]]) -> Dict[str, Union[Type[Enum], Type["IJsonEncodable"]]]:
        return {_type.__name__: _type for _type in key_types}

    @classmethod
    def _encode_prefix(cls) -> str:
        return f"{cls.__name__}::"

    @classmethod
    def _decompose_json(cls, json_string: str, key_types: Dict[
            str, Type[Union[Enum, IJsonEncodable]]]) -> (Dict[str, JsonCoder.SUPPORTED_TYPE]):
        """
        Utility method extracting the typical implementation of json_decode.
        """

        json_string = json_string.strip(cls._encode_prefix())[1:-1]
        merged_items = JsonCoder.split_commas_respect_parentheses(json_string)

        keys_and_values: Dict[str, JsonCoder.SUPPORTED_TYPE] = dict()
        for item in merged_items:
            key, value = item.split("=", maxsplit=1)
            keys_and_values[key] = JsonCoder.decode(value, key_types)

        return keys_and_values
