# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
from pprint import pprint

import pytest

from ..i_pytask_callback import IPyTaskCallback


class TestIPyTaskCallback(object):
    @staticmethod
    def setup_class(cls):
        cls.diagnostics_print = True

    @staticmethod
    def teardown_class(cls):
        pass

    def test_basics(self):
        # Interface documentation.
        if self.diagnostics_print:
            print('IPyTaskCallback interface documentation: ')
            print(IPyTaskCallback.__doc__)

        # Interface name and module.
        if self.diagnostics_print:
            print('IPyTaskCallback name: ', IPyTaskCallback.__name__)
            print('IPyTaskCallback module: ', IPyTaskCallback.__module__)

    def test_attributes(self):
        # Cannot use 'hasattr' since this object does not have a 'hasattrib' attribute.
        # Logical equivalent is use 'dir' or peek into the internal dictionary of the objects
        # attributes. In both cases, more than is probably wanted is returned.
        ipytask_attribs = dir(IPyTaskCallback)  # give the attributes of the IPyTaskCallback object
        ipytask_dict = IPyTaskCallback.__dict__
        if self.diagnostics_print:
            pprint(ipytask_attribs)
            pprint(ipytask_dict)
        assert 'progress_callback' in ipytask_attribs
        assert 'message_callback' in ipytask_attribs
        assert 'wrong_method' not in ipytask_attribs

    # You cannot call an abstract base class: '...unbound method...'.
    def test_just_an_interface(self):
        with pytest.raises(TypeError) as e:
            IPyTaskCallback.progress_callback()
        if self.diagnostics_print:
            print('exception raised: ', e)
