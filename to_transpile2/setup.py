# Copyright (c) 2016-2021 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
""" Example 'AutoStar style' setup.py.
"""
import sys
from pathlib import Path
from os import path


# noinspection DuplicatedCode
def _patch_msvc_compiler(optimize=False):
    """ Switches the Visual Studio compiler C optimization flag off / on.

    This is done by changing the flag in the distutils module source file so
    must be called before that module is imported.
    """
    print(f"setup._patch_msvc_compiler: optimize? {optimize}")
    print(f"    args: {sys.argv}")

    # targets used via Jenkins builds
    cython_commands = ["test", "cythonize", "cythonize_incremental"]
    cython_build = bool(set(sys.argv) & set(cython_commands))
    if not cython_build:
        print("setup._patch_msvc_compiler: not a Cython build so no compiler patch needed")
        return
    else:
        print("setup._patch_msvc_compiler: Cython build so compiler patch needed")

    # The distutils compiler file to be patched.
    target_file = Path(sys.executable).parent / "Lib/distutils/_msvccompiler.py"

    with open(str(target_file), "r", newline='') as f:
        content = f.read()

    on = "'/nologo', '/Ox', '/W3', '/GL', '/DNDEBUG'"  # /Ox: default optimization via distutils
    off = "'/nologo', '/Od', '/W3', '/GL', '/DNDEBUG'"  # /Od: optimization off
    content = content.replace(off, on) if optimize else content.replace(on, off)

    with open(str(target_file), "w", newline='') as f:
        f.write(content)
    print(f"setup._patch_msvc_compiler: set optimize {optimize} completed")


_patch_msvc_compiler(optimize=False)

from setuptools import setup, find_packages     # noqa
from setuptools.command.develop import develop  # noqa

from Cython.Distutils import build_ext          # noqa

# Add parent directory of this module to path: needed utility code lives outside the normal
# source tree.
sys.path.append(
    path.abspath(path.join(path.dirname(__file__), path.pardir)))
from setup_utilities import cythonize  # noqa 402

# Packages to cythonize protect company sensitive material.
CYTHON_INCLUDE_PACKAGES = [
    r'fei_xxx',
]

# Cython exclusions (package and modules) e.g.:
# * Issue at runtime when using RawImage: '_get_data() takes exactly one argument (0 given)'
#   Maybe it's due to the fact that C does not support defaults?
# * UI code excluded - issues at least with QThread class and signal handlers.
# * Simulate utilities code: walks the Python call stack so does not work as complied C code.

# Packages (directories) that should not be processed.
CYTHON_EXCLUDED_PACKAGES = [
    r'fei_common\applications\sherpa\ui\gen',
    r'fei_common\infra\tem_service\imaging',
]

# Modules (files) that should not be processed.
CYTHON_EXCLUDED_MODULES = [
    r'start_',
    r'signal_handler',
    r'main_window',
    r'generic_procedure',
    r'utilities',
    r'configure_cmd_files',  # excluded due to use of __file__ at module scope
    r'conftest.py',
]

# Items (directories and files) to exclude from the cythonized distributions.
DIST_EXCLUDED_PACKAGES = [
    '*.tests',
    '*.tests.*',
    'tests.*',
    'tests',
    'dev_*',
    r'adjust_build_info.*',
    r'Build-SherpaUiSource.*',
    # r'fei\autostar\applications\sherpa\plugins\dummy_plugin'
    r'conftest.py',
]

EXCLUDE_FOR_TEST = [
    'dev_*',
    r'adjust_build_info.*',
    r'Build-SherpaUiSource.*',
]

DIST_EXCLUDED_ITEMS_FROM_TEST_WHL = [
    r'tests',
    r'conftest.py',
]

_here = Path(__file__).resolve().parents[0]


class DevelopCommand(develop):
    """ Setuptools command to configure development setup.

    Sub-class of standard 'develop' command to allow additional custom code
    to be executed.
    """

    # Inheriting from old style Python class so no __init__ and super call.
    # def __init__(self):
    #     super(DevelopCommand, self).__init__()

    description = 'FEI AutoStar_Common wheel: "development mode".'

    def run(self):
        develop.run(self)
        if not self.uninstall:
            alt_script = '../python/utilities/Set-ShortcutsToCurrentPythonEnv.ps1'
            print("setup.py: NOTE: auto configure cmd/ps1 shortcuts disabled!")
            print(f"\t\tinstead use {alt_script}")

    def initialize_options(self):
        develop.initialize_options(self)

    def finalize_options(self):
        develop.finalize_options(self)


class CythonizeCommand(build_ext):
    """ Setuptools command to cythonize the application (without
    test directories, test scripts, and test applications).

    It converts tagged py files to Cython extensions and builds them.
    """

    # Inheriting from old style Python class so no __init__ and super call.
    # def __init__(self):
    #     super(DevelopCommand, self).__init__()

    description = 'FEI AutoStar_Common wheel: fully cythonized'

    def initialize_options(self):
        build_ext.initialize_options(self)

    def run(self):
        cythonize.build_cython_packages(self,
                                        root=_here,
                                        wheel_name="fei_xxx",
                                        dist_root_name="fei_xxx",
                                        dist_excluded_packages=DIST_EXCLUDED_PACKAGES,
                                        cython_include_packages=CYTHON_INCLUDE_PACKAGES,
                                        cython_excluded_packages=CYTHON_EXCLUDED_PACKAGES,
                                        cython_excluded_modules=CYTHON_EXCLUDED_MODULES,
                                        dist_excluded_items=DIST_EXCLUDED_ITEMS_FROM_TEST_WHL)


class CythonizeIncremental(build_ext):
    """ Setuptools command to incrementally cythonize only changed files
    """
    description = 'FEI AutoStar_Common wheel: fully cythonized'

    # Inheriting from old style Python class so no __init__ and super call.
    # def __init__(self):
    #     super(DevelopCommand, self).__init__()

    def initialize_options(self):
        build_ext.initialize_options(self)

    def run(self):
        cythonize.build_cython_packages(self,
                                        root=_here,
                                        wheel_name="fei_xxx",
                                        dist_root_name="fei_xxx",
                                        dist_excluded_packages=DIST_EXCLUDED_PACKAGES,
                                        cython_include_packages=CYTHON_INCLUDE_PACKAGES,
                                        cython_excluded_packages=CYTHON_EXCLUDED_PACKAGES,
                                        cython_excluded_modules=CYTHON_EXCLUDED_MODULES,
                                        incremental=True,
                                        dist_excluded_items=DIST_EXCLUDED_ITEMS_FROM_TEST_WHL)


class TestCommand(build_ext):
    """ Setuptools command for deployment in simulation mode.

    The application is still cythonized, but also test directories, test
    scripts, and test applications are part of the distribution. Test
    scripts and applications, however, are not cythonized.
    It converts tagged py files to Cython extensions and builds them.
    """

    # Inheriting from old style Python class so no __init__ and super call.
    # def __init__(self):
    #     super(DevelopCommand, self).__init__()

    description = 'FEI AutoStar_Common wheel: fully cythonized but test source'

    def initialize_options(self):
        build_ext.initialize_options(self)

    def run(self):
        cythonize.build_cython_packages(self,
                                        root=_here,
                                        wheel_name="fei_xxx",
                                        dist_root_name="fei_xxx",
                                        dist_excluded_packages=EXCLUDE_FOR_TEST,
                                        cython_include_packages=CYTHON_INCLUDE_PACKAGES,
                                        cython_excluded_packages=CYTHON_EXCLUDED_PACKAGES,
                                        cython_excluded_modules=CYTHON_EXCLUDED_MODULES)


setup(
    name="fei_xxx",

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="1.2.3",

    description="example dist - fei_xxx",
    long_description=f"example dist - fei_xxx ... for test purposes",

    # Install all packages (folders and files) in this folder.
    # https://pythonhosted.org/setuptools/setuptools.html#including-data-files
    packages=find_packages(where=".", exclude=["setup_utilities"]),

    cmdclass={
        "develop": DevelopCommand,
        "cythonize": CythonizeCommand,
        'test': TestCommand,
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
        #   .xml: XML file, used for configuration.
        #   .config: XML configuration file, used for DSAL Data Services logging.
        #   .csv: comma separated file used in tests.
        #   .dat: file containing test data.
        #   .emi: file containing test image(s).
        '': ['*.pyw', '*.pyd', '*.dll', '*.cmd', '*.ps1', '*.htm', '*.reg', '*.feature', '*.xml',
             '*.config', '*.csv', '*.dat', '*.emi'],
    },
)

_patch_msvc_compiler(optimize=True)
