# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
from pprint import pprint

import pytest

from ..i_pytask import IPyTask


class TestIPyTask(object):
    @staticmethod
    def setup_class(cls):
        cls.diagnostics_print = True

    @staticmethod
    def teardown_class(cls):
        pass

    def test_basics(self):
        # Interface documentation.
        if self.diagnostics_print:
            print('IPyTask interface documentation: ')
            print(IPyTask.__doc__)

        # Interface name and module.
        if self.diagnostics_print:
            print('IPyTask name: ', IPyTask.__name__)
            print('IPyTask module: ', IPyTask.__module__)

    def test_attributes(self):
        # Cannot use 'hasattr' since this object does not have a 'hasattrib' attribute.
        # Logical equivalent is use 'dir' or peek into the internal dictionary of the objects
        # attributes. In both cases, more than is probably wanted is returned.
        ipytask_attribs = dir(IPyTask)  # gives us the attributes of the IPyTask object
        ipytask_dict = IPyTask.__dict__
        if self.diagnostics_print:
            pprint(ipytask_attribs)
            pprint(ipytask_dict)
        # 'name' property: cannot be checked since it is only created in the __init__ method of
        # the IPyTask base class. I.e. can only verify it is preset on an instance of IPyTask,
        # not on IPyTask directly.
        # assert 'name' in IPyTask
        assert 'execute' in ipytask_attribs
        assert 'wrong_method' not in ipytask_attribs

    # You cannot call an abstract base class: '...unbound method...'.
    def test_just_an_interface(self):
        with pytest.raises(TypeError) as e:
            IPyTask.execute()
        if self.diagnostics_print:
            print('exception raised: ', e)
