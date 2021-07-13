# Copyright (c) 2021 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
""" Transpile, cythonize, some Python code.

For development / understanding purposes mainly, e.g. to step through in the
debugger.
"""
import sys
from datetime import datetime
from setuptools import setup
from pathlib import Path
from setuptools import Extension

from Cython.Build import cythonize


def create_extension(path, _dir):
    file_name = str(path.absolute())
    pdb_file_name = file_name.replace(".pyx", ".pdb")

    # Don't need to calculate module name if Extension calls is passed "*" for name.
    mod_name = file_name.replace(str(_dir.absolute()), "").replace(".pyx", "").replace("\\", ".")
    mod_name = mod_name[1:]
    print(f"extension details:")
    print(f"\tfile name: {file_name}")
    print(f"\tpdb name: {pdb_file_name}")
    print(f"\tmodule name: {mod_name}")

    return Extension(
        "*",  # gets converted to the full Python dotted name, e.g. my_utils.hello
        [file_name],
        libraries=["ole32", "oleaut32", "advapi32"],

        # -Zi: Leave optimization as is ('Ox' apparently) but generate full debug info.
        # -Fd: specify the intermediate pdb file -> essential for parallel builds
        extra_compile_args=["-Zi", f"-Fd{pdb_file_name}"],

        # /IGNORE:4197: suppress warning of function declared for export more than once
        # -debug=full: use debug info to create pdb files
        extra_link_args=["/IGNORE:4197", "-debug:full"],
    )


response = input("attach debugger to the Python process, then 'yes' to continue --> ")
if response[0].lower() != "y":
    print("exit without running script...")
    sys.exit(0)

start_time = datetime.now()
print(f"START: {start_time}")

this_dir = Path(__file__).parent
target_dir = Path(__file__).parent / "to_transpile2"
print(f"target pyx files in  dir: {target_dir}")

target_files = [create_extension(path, target_dir)
                for path in Path(target_dir).rglob("*.pyx")]

setup(
    ext_modules=cythonize(
        target_files,

        # Set language level to 3.X
        compiler_directives={'language_level': '3'},

        # add #line directives throughout the generated C/C++ code, 'semi-secret option' that
        # allows symbol mapping back to .pyx Python source. Cannot be used with with 'annotate'
        # option!
        emit_linenums=True,
    ),
)

print(f"START TIME:   {start_time}")
print(f"FINISH TIME:  {datetime.now()}")
