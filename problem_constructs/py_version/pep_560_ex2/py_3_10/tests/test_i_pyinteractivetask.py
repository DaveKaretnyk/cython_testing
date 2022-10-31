# Copyright (c) 2022 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

import pytest

from ..i_pyinteractivetask import IPyInteractiveTask


@pytest.fixture(scope="module")
def method_list():
    return [method for method in dir(IPyInteractiveTask)
            if method.startswith('_') is False]


def test_interface_methods(method_list):
    assert len(method_list) == 3
    assert 'provide_user_response' in method_list
    assert 'request_user_response' in method_list
    assert 'subscribe_user_response_requested' in method_list


def test_class_is_an_interface(method_list):
    with pytest.raises(TypeError) as e:
        IPyInteractiveTask[str, str]()

    assert all(method in str(e) for method in method_list)
