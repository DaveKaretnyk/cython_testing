""" Re-work of Cython.Build.Cythonize.py, which implements the 'cythonize.exe'
command line script published by the Cython package.

Summary:
Transpiles (cythonizes) all .pyx files in the directory given as input.
'tfs_cythonize --help' to show options.

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
import shutil
import tempfile
from datetime import datetime
from pprint import pprint
from pathlib import Path, PurePath
import multiprocessing
from setuptools import Extension
from distutils.core import setup

from Cython.Build.Dependencies import cythonize
from Cython.Compiler import Options as CythonOptions


mod_name = str(Path(__file__).stem)

# The CPU count is 'logical CPUs', e.g. 4 often means 2 cores each with hyper-threading.
parallel_compiles = multiprocessing.cpu_count()


def create_extension(target, package_root):
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

        # -Zi: Leave optimization as is ('Ox' apparently) but generate full debug info.
        # -Fd: specify the intermediate pdb file -> essential for parallel builds
        extra_compile_args=["-Zi", f"-Fd{target.replace('.pyx', '.pdb')}"],

        # /IGNORE:4197: suppress warning of function declared for export more than once
        # -debug=full: use debug info to create pdb files
        extra_link_args=["/IGNORE:4197", "-debug:full"],
    )


def parse_directives(option, name, value, parser):
    dest = option.dest
    old_directives = dict(getattr(parser.values, dest,
                                  CythonOptions.get_directive_defaults()))
    directives = CythonOptions.parse_directive_list(
        value, relaxed_bool=True, current_settings=old_directives)
    setattr(parser.values, dest, directives)


def parse_options(option, name, value, parser):
    dest = option.dest
    options = dict(getattr(parser.values, dest, {}))
    for opt in value.split(','):
        if '=' in opt:
            n, v = opt.split('=', 1)
            v = v.lower() not in ('false', 'f', '0', 'no')
        else:
            n, v = opt, True
        options[n] = v
    setattr(parser.values, dest, options)


def find_dist_base(path: PurePath) -> (PurePath, str):
    """ For the path supplied return the base directory and the root name of
    the package / dist as a tuple.

    E.g. For 'C:\\github\\AUTOSTAR\\AutoStar_Common\\python\\fei_common', the
    base directory is r'C:\\github\\AUTOSTAR\\AutoStar_Common\\python' and the
    package / distribution root name is 'fei_common'.

    This is different from the equivalent function in the Cython code base
    which computes the root name based on the location of the top most
    __init__.py file. For most AutoStar components that will not work.
    """
    return path.parent, path.stem


def cython_compile(path, options):
    pool = None
    try:
        base_dir, dist_root_name = find_dist_base(path)
        print(f"{mod_name}: creating setuptools.Extension instances:")
        targets = [create_extension(str(target), dist_root_name)
                   for target in path.rglob("*.pyx")]

        ext_modules = cythonize(
            targets,
            nthreads=options.parallel,
            exclude_failures=options.keep_going,
            exclude=options.excludes,
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


def run_distutils(args):
    base_dir, ext_modules = args
    script_args = ['build_ext', '-i']
    cwd = os.getcwd()
    temp_dir = None
    try:
        if base_dir:
            os.chdir(base_dir)
            temp_dir = tempfile.mkdtemp(dir=base_dir)
            script_args.extend(['--build-temp', temp_dir])
        setup(
            script_name='setup.py',
            script_args=script_args,
            ext_modules=ext_modules,
        )
    finally:
        if base_dir:
            os.chdir(cwd)
            if temp_dir and os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)


def build_args(args):
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] source_dir [options]')

    parser.add_option('-X', '--directive', metavar='NAME=VALUE,...', dest='directives',
                      type=str, action='callback', callback=parse_directives, default={},
                      help='set a compiler directive')
    parser.add_option('-s', '--option', metavar='NAME=VALUE', dest='options',
                      type=str, action='callback', callback=parse_options, default={},
                      help='set a cythonize option')
    parser.add_option('-3', '--python3', dest='python3_mode', action='store_true',
                      help='use Python 3 syntax mode by default')
    parser.add_option('-a', '--annotate', dest='annotate', action='store_true',
                      help='generate annotated HTML page for source files')

    parser.add_option('-x', '--exclude', metavar='PATTERN', dest='excludes',
                      action='append', default=[],
                      help='exclude certain file patterns from the compilation')

    parser.add_option('-b', '--build', dest='build', action='store_true',
                      help='build extension modules using distutils')
    parser.add_option('-j', '--parallel', dest='parallel', metavar='N',
                      type=int, default=parallel_compiles,
                      help=('run builds in N parallel jobs (default: %d)' %
                            parallel_compiles or 1))
    parser.add_option('-f', '--force', dest='force', action='store_true',
                      help='force recompilation')
    parser.add_option('-q', '--quiet', dest='quiet', action='store_true',
                      help='be less verbose during compilation')

    parser.add_option('--lenient', dest='lenient', action='store_true',
                      help='increase Python compatibility by ignoring some compile time errors')
    parser.add_option('-k', '--keep-going', dest='keep_going', action='store_true',
                      help='compile as much as possible, ignore compilation failures')

    options, args = parser.parse_args(args)  # if --help arg => print help and exit(0)
    if not args or len(args) != 1:
        parser.error("one source dir should be specified")
    path = Path(args[0]).resolve()
    if not path.is_dir():
        parser.error(f"not a valid source dir: {path}")
    if options.python3_mode:
        options.options['language_level'] = 3
    return path, options


def _delete_intermediate_pdb_files(path):
    # Note: deletion on Windows is not synchronous. OK here since the result of deleting is not
    # 'used immediately after the delete call'. Reliable solution in the AutoStar_Support
    # component if needed.
    int_pdbs = [int_pdb for int_pdb in Path(path).rglob("*.pdb")
                if not int_pdb.match("*win_amd64.pdb")]
    print(f"{mod_name}: remove {len(int_pdbs)} intermediate pdbs from: {path}")
    for int_pdb in int_pdbs:
        int_pdb.unlink()
        print(f"    deleted fle: {int_pdb}")


def _copy_final_pdb_files(path):
    int_sub_dir = r"build\lib.win-amd64-3.6"
    int_dir = Path(path).parent / int_sub_dir

    src_files = [src_file for src_file in int_dir.rglob("*.pdb")
                 if src_file.match("*win_amd64.pdb")]
    print(f"{mod_name}: copy {len(src_files)} final pdbs from intermediate dir: {int_dir}")
    for src_file in src_files:
        dst_file = Path(str(src_file).replace(int_sub_dir, ""))
        shutil.copy(src_file, dst_file)
        print(f"    dst file: {dst_file}")


def main(args=None):
    path, options = build_args(args)

    start_time = datetime.now()
    print(f"{mod_name} START TIME:   {start_time}")
    print(f"    available (logical) cpus: {parallel_compiles}")

    print(f"{mod_name}: source dir: {path}")
    print(f"{mod_name}: options:")
    pprint(options.__dict__, indent=4)

    if options.annotate:  # can only be annotate or emit_linenums, not both
        CythonOptions.annotate = True

    cython_compile(path, options)
    _delete_intermediate_pdb_files(path)
    _copy_final_pdb_files(path)

    print(f"{mod_name} START TIME:   {start_time}")
    print(f"{mod_name} FINISH TIME:  {datetime.now()}")


if __name__ == '__main__':
    main()
