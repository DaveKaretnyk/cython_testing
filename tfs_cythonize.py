""" Re-work of Cython.Build.Cythonize.py, which implements the 'cythonize.exe'
command line script published by the Cython package.

Summary:
Transpiles (cythonizes) all .pyx files in the directory given as input.
'tfs_cythonize --help' to show options:
    * --annotate: generate annotated HTML page for C source files, DO NOT USE
                  in production since it disables mapping back to .pyx files
                  from generated symbols (pdbs)
    * --parallel: run C compilation in parallel (int) experimental, DO NOT USE
                  in production builds for now
    * --force: rebuild even if not source file changes
    * --quiet: less verbose during Cython compile (no effect on C compile)

Prerequisites:
* Visual Studio 2017 must be installed on the system.
* The required environment variables for running the Visual Studio compiler
  from the command line must be defined. I.e. VCVARSALL.BAT should have been
  run.
* Also the following key env. vars must be set (these are not set by
  VCVARSALL.BAT):
    $ENV:DISTUTILS_USE_SDK = 1
    $ENV:PY_VCRUNTIME_REDIST='No thanks'

For AutoStar purposes there is no need to be provide such a generic API. In
fact certain compiler directives must be be precisely controlled and should
not be changed.

Background:
Parallel building of Cython extensions is not supported when using setup
'commands'. Specifically commands that are specializations of
Cython.Distutils.build_ext.new_build_ext are not supported as commands. Hence
a modified version of Cython.Build.Cythonize.py is used instead.

Additionally the code currently executed in the context of an AutoStar
'setup.py(...)' call is overly complicated and needs simplification. E.g.
support is in there for handling: source dists; Cython test dists; Cython
product dists from test dists; pdb files needed for post-mortem debugging;
and incremental building. And lastly, the use of a standard setup.py longer
term is not useful for Anaconda distribution management.

Key specific changes to Cython.Build.Cythonize.py:
* Building inplace (i.e. pyd next to the Python source) does not work when
  using 'pythons setup.py build_ext --inplace' since this bypasses the logic
  in the Cython code.
* There is no need to support a 'wide range' of Python versions. E.g. AutoStar
  does not need to support earlier than 3.6.

"""
import os
import sys
import atexit
import shutil
import tempfile
from datetime import datetime
from pprint import pprint
from pathlib import Path, PurePath
import multiprocessing
from argparse import ArgumentParser
from typing import Any, Dict, List, Tuple

mod_name = str(Path(__file__).stem)


# noinspection DuplicatedCode
def _patch_msvc_compiler(optimize: bool = False) -> None:
    """ Switches the Visual Studio compiler C optimization flag on / off.

    This is done by changing the flag in the distutils module source file so
    must be called before that module is imported.

    :param optimize: switch optimization on/off
    """
    print(f"{mod_name}._patch_msvc_compiler: optimize? {optimize}")

    # The distutils compiler file to be patched.
    target_file = Path(sys.executable).parent / "Lib/distutils/_msvccompiler.py"

    with open(str(target_file), "rt", newline='', encoding="utf-8") as f:
        content = f.read()

    on = "'/nologo', '/Ox', '/W3', '/GL', '/DNDEBUG'"  # /Ox: default optimization via distutils
    off = "'/nologo', '/Od', '/W3', '/GL', '/DNDEBUG'"  # /Od: optimization off
    content = content.replace(off, on) if optimize else content.replace(on, off)

    with open(str(target_file), "wt", newline='', encoding="utf-8") as f:
        f.write(content)
    print(f"{mod_name}._patch_msvc_compiler: set optimize {optimize} completed")


_patch_msvc_compiler(optimize=False)

from setuptools import Extension                        # noqa
from distutils.core import setup                        # noqa

from Cython.Build.Dependencies import cythonize         # noqa
from Cython.Compiler import Options as CythonOptions    # noqa


class TranspileDirectives:
    """ Define the Cython build transpile directives.

    * path is mandatory & must be supplied as a positional command line arg.
    * some directives can be optionally supplied on the commend line.
    * some directives are only defined here, i.e. cannot be specified on command
      line.
    """
    def __init__(self) -> None:
        self.path = None
        """ Path (dir) to process"""

        # These args are only defined here.
        self.directives = {
            # language level to 3.X, else prints with keyword parameters do not compile
            'language_level':           3,
            # allow functions with single positional para to be called with single keyword para
            'always_allow_keywords':    False,
        }
        self.options: Dict[Any, Any] = {}
        self.build = True
        self.lenient = None
        self.keep_going = None
        self.emit_linenums = True
        self.excludes: List[str] = []

        # These args might be supplied via the command line.
        self.parallel = 0
        self.annotate = False
        self.force = False
        self.quiet = False
        self.single_keyword_arg = False


def create_extension(target: str, package_root: str) -> Extension:
    """ For the target directory and package root supplied return a setuptools
    Extension instance.

    * The extension instance defines how the generated C source file will be
      compiled.
    * Key compiler directives are hardcoded in this function.
    * Package root name: e.g. 'fei_common' or 'fei_stage. Needed to compute
      the full dotted name for the module. For example:
      'fei_common.infra.tem_service.api'.

    :param target: .pyx file to be processed
    :param package_root: root name of the package
    :return: object defining how the file will be built
    """
    if package_root not in target:
        raise ValueError(f"'{package_root}' not found in file name: '{target}'")

    # Strip anything before package root.
    # E.g. "C:\\work_dir\\fei_some_comp\\a\\b\\hello.pyx" -> "fei_some_comp\\a\\b\\hello.pyx"
    mod_file_name = target.replace(target.split(package_root)[0], "")

    module_name = mod_file_name.replace(".pyx", "").replace("\\", ".")
    print(f"    target file:                {target}")
    print(f"    module full dotted name:    {module_name}")

    return Extension(
        module_name,
        [target],
        libraries=["ole32", "oleaut32", "advapi32"],

        # -Od: i.e. no compiler optimization, 'Ox' is the default hard coded into distutils:
        #  distutils._msvccompiler.MSVCCompiler.
        # -Zi: Leave optimization as is ('Ox' apparently) but generate full debug info.
        # -Fd: specify the intermediate pdb file -> essential for parallel builds
        extra_compile_args=["-Zi", "-Od", f"-Fd{target.replace('.pyx', '.pdb')}"],

        # /IGNORE:4197: suppress warning of function declared for export more than once
        # -debug=full: use debug info to create pdb files
        extra_link_args=["/IGNORE:4197", "-debug:full"],
    )


def find_dist_base(path: PurePath) -> Tuple[PurePath, str]:
    """ For the path supplied return the base directory and the root name of
    the package / dist as a tuple.

    E.g. For 'C:\\github\\AUTOSTAR\\AutoStar_Common\\python\\fei_common', the
    base directory is r'C:\\github\\AUTOSTAR\\AutoStar_Common\\python' and the
    package / distribution root name is 'fei_common'.

    This is different from the equivalent function in the Cython code base
    which computes the root name based on the location of the top most
    __init__.py file. For most AutoStar components that will not work.

    :param path: the directory to be processed
    :return base: directory and package root
    """
    return path.parent, path.stem


def cython_compile(path: Path, options: TranspileDirectives) -> int:
    """ Perform the Cython build of all .pyx files in the supplied directory
    using the directives supplied. Return the number of files processed.

    :param path: directory to be processed
    :param options: directives to be used in the build
    :return 0 if ok, non-zero if problems
    """
    pool = None
    try:
        base_dir, dist_root_name = find_dist_base(path)
        print(f"{mod_name}: creating setuptools.Extension instances:")
        targets = [create_extension(str(target), dist_root_name)
                   for target in path.rglob("*.pyx")]
        num_files_compiled = len(targets)

        ext_modules = cythonize(
            targets,
            nthreads=options.parallel,
            exclude_failures=options.keep_going,
            exclude=options.excludes,
            emit_linenums=options.emit_linenums,
            annotate=options.annotate,
            compiler_directives=options.directives,
            force=options.force,
            quiet=options.quiet,
            **options.options)

        if ext_modules and options.build:
            if len(ext_modules) > 1 and options.parallel > 1:
                if pool is None:
                    pool = multiprocessing.Pool(options.parallel)
                pool.map_async(run_distutils, [
                    (str(base_dir), [ext]) for ext in ext_modules])
            else:
                run_distutils((str(base_dir), ext_modules))
    except Exception:
        if pool is not None:
            pool.terminate()
        raise
    else:
        if pool is not None:
            pool.close()
            pool.join()

    return num_files_compiled


def run_distutils(args) -> None:
    """ Run distutils on the args supplied.

    * args is a tuple of base directory & module list.
    * args are passed like this to allow use of pool.map_aysnc when compiling
      the modules in parallel with multiple processes.

    :param args: tuple of base directory and module list
    """
    base_dir, ext_modules = args
    script_args = ['build_ext', '-i']
    cwd = os.getcwd()
    temp_dir = None
    try:
        if base_dir:
            os.chdir(base_dir)
            temp_dir = tempfile.mkdtemp(dir=base_dir)
            script_args.extend(['--build-temp', temp_dir])
        setup(script_name='setup.py', script_args=script_args, ext_modules=ext_modules,
        )
    finally:
        if base_dir:
            os.chdir(cwd)
            if temp_dir and os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)


def construct_directives() -> Tuple[Path, TranspileDirectives]:
    """ Construct the build directives to use from the command line arguments
    supplied to the program.

    * Some build directives are supplied on the command line.
    * Some build directives are hardcoded in this function

    :return path: to be processed & directives to build with
    """
    parser = ArgumentParser(
        description="Cython build all pyx files in the supplied directory (recursively)")
    parser.add_argument("path", type=str, help="the path (directory) to be processed")
    parser.add_argument("-f", "--force", dest="force", action="store_true",
                        help="force recompilation")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                        help="less verbose during Python to C translation "
                             "(no effect on C compilation)")
    parser.add_argument("-j", "--parallel", dest="parallel", metavar="N",
                        type=int, default=0,
                        help="run builds in N parallel jobs (default is 0 -> no parallelization)"
                             "experimental, DO NOT USE in production builds for now")
    parser.add_argument("-a", "--annotate", dest="annotate", action="store_true",
                        help="generate annotated HTML for C source files "
                             "(use for diagnostics only, DO NOT USE in production builds)")
    parser.add_argument("-s", "--single_keyword_arg", dest="single_keyword_arg",
                        action="store_true",
                        help="set directive always_allow_keywords "
                             "(for experimentation only, DO NOT USE in production builds)")

    my_directives = parser.parse_args(namespace=TranspileDirectives())
    if my_directives is None or my_directives.path is None:
        parser.error("problems parsing args!")
    path = Path(my_directives.path).resolve()
    if not path.is_dir():
        parser.error(f"not a valid source dir: {path}")

    if my_directives.annotate:
        CythonOptions.annotate = True
        print(f"{mod_name}: WARNING:emit_linenums disabled because annotate option selected")
        print(f"{mod_name}:     this prevents post-mortem debugging back to .pyx source")
        print(f"{mod_name}:     should no be used in production builds")
        my_directives.emit_linenums = False

    if my_directives.single_keyword_arg:
        my_directives.directives['always_allow_keywords'] = True
        print(f"{mod_name}: WARNING:directive always_allow_keywords is True")
        print(f"{mod_name}:     should no be used in production builds")

    return path, my_directives


def delete_intermediate_pdb_files(path: Path) -> None:
    """  Delete all intermediate pdb files from the path supplied.

    Note: deletion on Windows is not synchronous. OK here since the result of
    deleting is not 'used immediately after the delete call'. Reliable
    solution in the AutoStar_Support component if needed.

    :param path: directory to be processed
    """
    int_pdbs = [int_pdb for int_pdb in Path(path).rglob("*.pdb")
                if not int_pdb.match("*win_amd64.pdb")]
    print(f"{mod_name}: remove {len(int_pdbs)} intermediate pdbs from: {path}")
    for int_pdb in int_pdbs:
        int_pdb.unlink()
        print(f"    deleted fle: {int_pdb}")


def copy_final_pdb_files(path: Path) -> None:
    """For the path supplied copy the final .pdb files to the same location as
    the corresponding .pyx files.

    :param path: directory to be processed
    """
    int_sub_dir = r"build\lib.win-amd64-3.6"
    int_dir = Path(path).parent / int_sub_dir

    src_files = [src_file for src_file in int_dir.rglob("*.pdb")
                 if src_file.match("*win_amd64.pdb")]
    print(f"{mod_name}: copy {len(src_files)} final pdbs from intermediate dir: {int_dir}")
    for src_file in src_files:
        dst_file = Path(str(src_file).replace(int_sub_dir, ""))
        shutil.copy(src_file, dst_file)
        print(f"    dst file: {dst_file}")


def check_results(path: Path, num_files_compiled: int) -> int:
    """ Check that the number of pyd & pdb files generated equals the number
    of source files that were compiled. Return 0 if OK else return non-zero.

    :param path: directory to be processed
    :param num_files_compiled: expected number of files
    :return 0 if OK, non-zero if not
    """
    num_pdbs = len([pdb for pdb in path.rglob("*.pdb")])
    num_pyds = len([pyd for pyd in path.rglob("*.pyd")])
    print(f"{mod_name}: check compilation results:")
    print(f"    source files: {num_files_compiled}")
    print(f"    pdb files:    {num_pdbs}")
    print(f"    pyd files:    {num_pyds}")

    exit_code = 5
    if num_files_compiled == num_pdbs == num_pyds:
        exit_code = 0
    else:
        print(f"{mod_name}: ERROR: wrong number of pyd or pdb files generated")
    return exit_code


def main():
    # Undo the compiler path: this will handle most exits of the program apart
    # from 'really bad crashes', see atexit docs.
    atexit.register(_patch_msvc_compiler, optimize=True)
    path, directives = construct_directives()

    start_time = datetime.now()
    print(f"{mod_name} START TIME:   {start_time}")
    print(f"    available (logical) cpus: {multiprocessing.cpu_count()}")

    print(f"{mod_name}: source dir: {path}")
    print(f"{mod_name}: directives:")
    pprint(directives.__dict__, indent=4)

    num_files_compiled = cython_compile(path, directives)
    delete_intermediate_pdb_files(path)
    copy_final_pdb_files(path)
    success = check_results(path, num_files_compiled)

    print(f"{mod_name} START TIME:   {start_time}")
    print(f"{mod_name} FINISH TIME:  {datetime.now()}")

    sys.exit(success)


if __name__ == '__main__':
    main()
