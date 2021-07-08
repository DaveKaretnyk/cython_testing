from datetime import datetime
from setuptools import setup
from pathlib import Path
from pprint import pprint
from setuptools import Extension

from Cython.Build import cythonize


def create_extension(path, _dir):
    file_name = str(path.absolute())
    pdb_file_name = file_name.replace(".pyx", ".pdb")
    # print(f"_dir: {_dir}")
    # print(f"file_name: {file_name}")

    mod_name = file_name.replace(str(_dir.absolute()), "").replace(".pyx", "").replace("\\", ".")
    mod_name = mod_name[1:]
    print(mod_name)

    return Extension(
        mod_name,  # ???
        [file_name],  # ???
        libraries=["ole32", "oleaut32", "advapi32"],

        # -Zi: Leave optimization as is ('Ox' apparently) but generate full debug info.
        # -Fd: specify the intermediate pdb file -> essential for parallel builds
        extra_compile_args=["-Zi", f"-Fd{pdb_file_name}"],

        # /IGNORE:4197: suppress warning of function declared for export more than once
        # -debug=full: use debug info to create pdb files
        extra_link_args=["/IGNORE:4197", "-debug:full"],
    )


start_time = datetime.now()
print(f"START: {start_time}")

this_dir = Path(__file__).parent
target_dir = Path(__file__).parent / "to_transpile"
# target_files = [str(path.absolute()) for path in Path(target_dir).glob("*.pyx")]
# target_files = [create_extension(str(path.absolute()))
#                 for path in Path(target_dir).glob("*.pyx")]
target_files = [create_extension(path, target_dir)
                for path in Path(target_dir).rglob("*.pyx")]
print(f"target pyx files to process from dir: {target_dir}")
pprint(target_files)

# ??? get .pyd in same directory as source?
setup(
    ext_modules=cythonize(
        target_files,

        # Set language level to 3.X, else prints with keyword parameters do not compile.
        compiler_directives={'language_level': '3'},

        # add #line directives throughout the generated C/C++ code, 'semi-secret option' that
        # allows symbol mapping back to .pyx Python source. Cannot be used with with 'annotate'
        # option!
        emit_linenums=True,
    ),
)

print(f"START TIME:   {start_time}")
print(f"FINISH TIME:: {datetime.now()}")
