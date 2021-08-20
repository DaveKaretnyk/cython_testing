# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
""" Distribution creation for Cythonize test wheel.
"""
from os import path

from Cython.Distutils import build_ext
from setuptools import setup, find_packages

from utilities.cython import cythonize

# Explicitly list the packages to cythonize and keep them to the bare minimum needed to protect
# company sensitive material.
#
# Some packages not cythonized because they cause issues at runtime: PySide connect issue;
# function being converted to builtin_function_or_method type; trouble with Enthought traits.
#
CYTHON_INCLUDE_PACKAGES = [
    r'test_dist\included_package'
]

# Packages (directories) that should not be processed.
CYTHON_EXCLUDED_PACKAGES = [
    r'test_dist\excluded_package'
]

# Modules (files) that should not be processed.
CYTHON_EXCLUDED_MODULES = [
    r'excluded_',
]

# Items (directories and files) to exclude from the cythonized distributions.
DIST_EXCLUDED_PACKAGES = [
    '*.tests',
    '*.tests.*',
    'tests.*',
    'tests',
]

here = path.abspath(path.dirname(__file__))


class CythonizeCommand(build_ext):
    """ Setuptools command to cythonize the application (without
    test directories, test scripts, and test applications).

    It converts tagged py files to Cython extensions and builds them.
    """
    # Inheriting from old style Python class so no __init__ and super call.
    # def __init__(self):
    #     super(CythonizeCommand, self).__init__()

    description = 'test wheel: fully cythonized'

    def initialize_options(self):
        build_ext.initialize_options(self)

    def run(self):
        cythonize.build_cython_packages(self,
                                        here,
                                        DIST_EXCLUDED_PACKAGES,
                                        CYTHON_INCLUDE_PACKAGES,
                                        CYTHON_EXCLUDED_PACKAGES,
                                        CYTHON_EXCLUDED_MODULES)


class CythonizeIncremental(build_ext):
    """ Setuptools command to incrementally cythonize only changed files
    """
    description = 'test wheel: fully cythonized'

    def initialize_options(self):
        build_ext.initialize_options(self)

    def run(self):
        cythonize.build_cython_packages(self,
                                        here,
                                        DIST_EXCLUDED_PACKAGES,
                                        CYTHON_INCLUDE_PACKAGES,
                                        CYTHON_EXCLUDED_PACKAGES,
                                        CYTHON_EXCLUDED_MODULES,
                                        True)


setup(
    name='test_dist',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.0',

    description='test_dist 1.0.0',
    long_description='test distribution for cythonization unit test',

    # The project's main homepage.
    url='https://bro-gitlab.w2k.feico.com/COMPONENTS/AUTOSTAR',

    # Author details
    author='FEI',
    author_email='AutoStar@fei.com',

    # Choose your license
    license='FEI',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: FEI',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='Cythonize',

    # Install all packages (folders and files) in this folder.
    # https://pythonhosted.org/setuptools/setuptools.html#including-data-files
    packages=find_packages(where='.'),

    cmdclass={
        'cythonize': CythonizeCommand,
        'cythonize_incremental': CythonizeIncremental
    },

    package_data={
        # Files with these extensions in any package will be included.
        #   .pyw: Python source that can be launched without a command shell popping up.
        #   .pyd: typically a binary extension dll.
        #   .dll: dll binary.
        #   .cmd: Script file, e.g. for running a Python script.
        #   .ps1: PowerShell file, e.g. for running a Python script.
        #   .htm: used for help documentation.
        #   .reg: RegEdit 5 file, e.g. used to set logging options for some dev tools.
        #   .feature: BDD feature file, containing test script in Gherkin language.
        '': ['*.pyw', '*.pyd', '*.dll', '*.cmd', '*.ps1', '*.htm', '*.reg', '*.feature'],
    },
)
