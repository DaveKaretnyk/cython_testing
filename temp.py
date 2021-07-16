from pprint import pprint
import glob
from pathlib import Path
from pprint import pprint
from setuptools import Extension
import os

if __name__ == '__main__':
    target_dir = Path(__file__).parent / "to_transpile"

    target_files = [str(path.absolute()) for path in Path(target_dir).glob("*.pyx")]
    print(f"target pyx files to process from dir: {target_dir}")
    pprint(target_files)

    cython_extension_directories = []
    for dirpath, directories, files in os.walk(target_dir):
        # if the directory contains pyx files, cythonize it
        if len(glob.glob('{0}/*.pyx'.format(dirpath))) > 0:
            cython_extension_directories.append(dirpath)
    print("************")
    pprint(cython_extension_directories)
    print("************: dirpath")
    print(dirpath)
    print(['{}/*.pyx'.format(dirpath)])
    print("************: directories")
    print(directories)
    print("************: files")
    print(files)

    my_list = [
        Extension(
            '*',
            ['{}/*.pyx'.format(dirpath)],
            libraries=['ole32', 'oleaut32', 'advapi32'],

            # Leave optimization as is ('Ox' apparently) but generate full debug info.
            extra_compile_args=['-Zi'],

            # /IGNORE:4197: suppress warning of function declared for export more than once
            # -debug=full: use debug info to create pdb files
            extra_link_args=['/IGNORE:4197', '-debug:full'],

        )
        for dirpath in cython_extension_directories
    ]

    target_files = [str(path.absolute()).replace(".pyx", ".pdb")
                    for path in Path(target_dir).rglob("*.pyx")]
    print(f"target pyx files to process from dir: {target_dir}")
    pprint(target_files)

    target_files = [str(path.absolute()).
                    replace(str(target_dir), "").
                    replace(".pyx", "").
                    replace("\\", ".")
                    for path in Path(target_dir).rglob("*.pyx")]
    print(f"target pyx files to process from dir: {target_dir}")
    pprint(target_files)

    # os.system('set')

    from multiprocessing import cpu_count
    # This seems to be the number of logical CPUs.
    print(f"multiprocessing module says cpu count is: {cpu_count()}")

    path = Path(__file__).parent / "to_transpile2"
    paths = [os.path.join(str(path), "**" ".{py,pyx}")]
    print(paths)

