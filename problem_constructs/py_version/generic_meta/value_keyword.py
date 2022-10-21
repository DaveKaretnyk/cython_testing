#  Copyright (c) 2020 by Thermo Fisher Scientific
#  All rights reserved. This file includes confidential and proprietary information
#  of Thermo Fisher Scientific
from abc import abstractmethod
from collections.abc import Hashable
from enum import Enum
from typing import Dict, Generic, Type, TypeVar, Union

from numpy import inf

from .i_json_encodable import IJsonEncodable
from .json_encodable import JsonEncodable

_T = TypeVar("_T")


# pylint: disable=inherit-non-class
class ValueKeyWord(Hashable, JsonEncodable, Generic[_T]):
    _type_length = 0  # defined in each child class

    @classmethod
    def __len__(cls):
        return cls._type_length

    def __init__(self, value: _T) -> None:
        super(ValueKeyWord, self).__init__()
        self.value = value

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __ne__(self, other) -> bool:
        return not self == other

    def __repr__(self) -> str:
        return "{}({})".format(self.__class__.__name__, self.value)

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        return hash(self.__class__) ^ hash(self.value)

    @classmethod
    @abstractmethod
    def json_decode(cls, json_string: str, key_types: Dict[str, Union[Type[Enum], Type[
            IJsonEncodable]]]) -> "ValueKeyWord":
        """
        Individually defined in every child, way to rebuild the structure from json string.
        :param json_string: (str)
        :param key_types: dictionary of names and enum types for the inner-value decoding
        :return: (fei_smali.infra.constants_support.value_keyword.ValueKeyWord)
        """

    def json_encode(self) -> str:
        """
        Way to encode the structure to json compatible string.
        :return:
        """
        return self._encode_prefix() + str(self.value)


class GunLensKeyWord(ValueKeyWord[float]):
    _type_length = 8

    @classmethod
    def json_decode(cls, json_string: str, key_types: Dict[str, Union[Type[Enum], Type[
            IJsonEncodable]]]) -> "GunLensKeyWord":
        return cls(float(json_string))


class ImageCorrectorKeyWord(ValueKeyWord[bool]):
    _type_length = 2

    @classmethod
    def json_decode(cls, json_string: str,
                    key_types: Dict[str, Union[Type[Enum], Type[IJsonEncodable]]]) -> (
            "ImageCorrectorKeyWord"):
        return cls(bool(json_string))


class ProbeCorrectorKeyWord(ValueKeyWord[bool]):
    _type_length = 2

    @classmethod
    def json_decode(cls, json_string: str,
                    key_types: Dict[str, Union[Type[Enum], Type[IJsonEncodable]]]) -> (
            "ProbeCorrectorKeyWord"):
        return cls(bool(json_string))


class SpotSizeKeyWord(ValueKeyWord[int]):
    _type_length = 11

    @classmethod
    def json_decode(cls, json_string: str, key_types: Dict[str, Union[Type[Enum], Type[
            IJsonEncodable]]]) -> "SpotSizeKeyWord":
        return cls(int(json_string))


class MagnificationIndexKeyWord(ValueKeyWord[int]):
    _type_length = 16

    @classmethod
    def json_decode(cls, json_string: str,
                    key_types: Dict[str, Union[Type[Enum], Type[IJsonEncodable]]]) -> (
            "MagnificationIndexKeyWord"):
        return cls(int(json_string))


class MagnificationKeyWord(ValueKeyWord[Union[int, float]]):
    _type_length = inf

    @classmethod
    def json_decode(cls, json_string: str, key_types: Dict[str, Union[Type[Enum], Type[
            IJsonEncodable]]]) -> "MagnificationKeyWord":
        return cls(float(json_string))


class MicroscopeTypeKeyWord(ValueKeyWord[str]):
    _type_length = inf

    @classmethod
    def json_decode(cls, json_string: str, key_types: Dict[str, Union[Type[Enum], Type[
            IJsonEncodable]]]) -> "MicroscopeTypeKeyWord":
        return cls(json_string)


class FringeFreeIlluminationKeyWord(ValueKeyWord[bool]):
    _type_length = 2

    @classmethod
    def json_decode(cls, json_string: str, key_types: Dict[str, Union[Type[Enum], Type[
            IJsonEncodable]]]) -> "FringeFreeIlluminationKeyWord":
        return cls(bool(json_string))
