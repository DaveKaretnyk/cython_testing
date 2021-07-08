from datetime import datetime
from setuptools import setup
from pathlib import Path

from Cython.Build import cythonize

this_dir = Path(__file__).parent
print(this_dir)
target_dir = Path(__file__).parent / "to_transpile"

start_time = datetime.now()
print(f"START: {start_time}")

_name = "cython_test"
_version = "0.6.6"

setup(
    name=_name,
    version=_version,
    long_descriptio=f"{_name} {_version}",
    cmdclass={},

    ext_modules=cythonize(
        [
            str(target_dir / "hello0.pyx"),
            str(target_dir / "hello1.pyx"),
            str(target_dir / "hello2.pyx"),
            str(target_dir / "hello3.pyx"),
            str(target_dir / "hello4.pyx"),
            # str(target_dir / "hello5.pyx"),
            # str(target_dir / "hello6.pyx"),
            # str(target_dir / "hello7.pyx"),
            # str(target_dir / "hello8.pyx"),
            # str(target_dir / "hello9.pyx"),
        ],
        # nthreads=4
    ),
    zip_safe=False
)

print(f"START TIME:   {start_time}")
print(f"FINISH TIME:: {datetime.now()}")
