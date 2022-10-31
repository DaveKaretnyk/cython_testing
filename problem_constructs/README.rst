Problematic language constructs
===============================
Constructs that cause problems for the Cython transpile process are in this
directory.

Code should run OK from PyCharm, VS code, etc but are mainly meant for running
from the command line.

cy_version
----------
This directory contains the Cython version of the problematic code, so .pyx
files for the key modules.

Obviously the modules need first compiled to the .pyd file. E.g. see script
'Invoke-Cythonize.py' in the root directory of this repository.

py_version
----------
This directory contains the Python version of problematic code, so .py files.
Useful for cross-checking purposes.
