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
    # print(f"target pyx files to process from dir: {target_dir}")
    # pprint(target_files)

    # os.system('set')

    from multiprocessing import cpu_count
    # This seems to be the number of logical CPUs.
    print(f"multiprocessing module says cpu count is: {cpu_count()}")

    # target_dir = Path(__file__).parent / "to_transpile"
    # file_names = [str(file_name.resolve()) for file_name in Path(target_dir).rglob("*.pyx")]
    # pprint(file_names)
    # print(len(file_names))

    target = "C:\\a\\b\\c\\hello.pyx"
    print(target)
    pdb_name = f"-Fd{target.replace('.pyx', '.pdb')}"
    print(target)
    print(pdb_name)

    # Don't need to calculate module name if Extension calls is passed "*" for name.
    dist_name = "fei_some_comp"
    #  _dir = "C:\\work_dir\\fei_some_comp"
    file_name = f"C:\\work_dir\\fei_some_comp\\a\\b\\c\\hello.pyx"
    mod_file_name = file_name.replace(file_name.split(dist_name)[0], "")
    # mod_file_name = file_name[file_name.find(dist_name):]
    mod_name = mod_file_name.replace(".pyx", "").replace("\\", ".")
    # mod_name = mod_name[1:]  # get rid of leading . in name
    # print(f"_dir:               {_dir}")
    print(f"file_name:              {file_name}")
    print(f"module file name:       {mod_file_name}")
    print(f"module dotted name:     {mod_name}")

    x = file_name.split(dist_name)
    print(x)
