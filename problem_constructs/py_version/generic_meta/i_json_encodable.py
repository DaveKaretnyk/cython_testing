#  Copyright (c) 2020 by Thermo Fisher Scientific
#  All rights reserved. This file includes confidential and proprietary information
#  of Thermo Fisher Scientific
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Type, Union


class IJsonEncodable(ABC):
    @classmethod
    @abstractmethod
    def json_decode(cls, json_string: str, key_types: Dict[str, Union[Type[Enum], Type[
            "IJsonEncodable"]]]) -> "IJsonEncodable":
        """
        Method to decode json compatible string into the structure.
        :return: IJsonEncodable instance created from the json_string
        """

    @abstractmethod
    def json_encode(self) -> str:
        """
        Method to encode the structure to string compatible with json. The prefix must be have form
        of classname::anything. The classname:: part is for KeyWordsMapHelper to determine what type
        shall be used for calling json_decode.
        :return: string representation of IJsonEncodable object
        """
