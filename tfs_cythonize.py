""" Re-work of Cython.Build.Cythonize.py, which implements the 'cythonize.exe'
command line script published by the Cython package.

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
  using 'pythons setup.py build_ext' --inplace' since this bypasses the logic
  for inplace building present in the Cython code.
* There is no need to support a 'wide range' of Python versions. E.g. AutoStar
  does not need to support earlier than 3.6.

"""
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
import multiprocessing
from setuptools import Extension
from distutils.core import setup

from Cython.Build.Dependencies import cythonize
from Cython.Compiler import Options


mod_name = str(Path(__file__).stem)

# The CPU count is 'logical CPUs', e.g. 4 often means 2 cores each with hyper-threading.
parallel_compiles = multiprocessing.cpu_count()
print(f"{mod_name}: available (logical) cpus: {parallel_compiles}")


def create_extension(target, package_root):
    if package_root not in target:
        raise ValueError(f"'{package_root}' not found in file name: '{target}'")

    # Strip anything before package root.
    # E.g. "C:\\work_dir\\fei_some_comp\\a\\b\\hello.pyx" -> "fei_some_comp\\a\\b\\hello.pyx"
    mod_file_name = target.replace(target.split(package_root)[0], "")

    mod_name = mod_file_name.replace(".pyx", "").replace("\\", ".")
    print(f"target file:                {target}")
    print(f"module full dotted name:    {mod_name}")

    return Extension(
        mod_name,
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
                                  Options.get_directive_defaults()))
    directives = Options.parse_directive_list(
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


def find_dist_base(path: str) -> (str, str):
    """ For the path supplied return the base directory and the root name of
    the package / dist as a tuple.

    The package/dist root name is the top level directory containing a
    __init__.py file and the base directory is the parent directory of that
    dir.

    E.g. For 'C:\\github\\AUTOSTAR\\AutoStar_Common\\python\\fei_common', the
    base directory is r'C:\\github\\AUTOSTAR\\AutoStar_Common\\python' and the
    package / distribution root name is 'fei_common'.
    """
    path = path.rstrip(os.path.sep)
    base_dir, package_root = os.path.split(path)
    while os.path.isfile(os.path.join(base_dir, '__init__.py')):
        base_dir, parent = os.path.split(base_dir)
        package_root = '%s/%s' % (parent, package_root)
    return base_dir, package_root


def cython_compile(path, options):
    pool = None
    abs_path = os.path.abspath(path)
    try:
        if not options.build_inplace:
            raise ValueError("building must be inplace")

        base_dir, dist_root_name = find_dist_base(abs_path)
        if os.path.isdir(abs_path):
            # process a directory recursively
            targets = [create_extension(str(target), dist_root_name)
                       for target in Path(abs_path).rglob("*.pyx")]
        else:
            targets = [abs_path]  # process a file

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
                    (base_dir, [ext]) for ext in ext_modules])
            else:
                run_distutils((base_dir, ext_modules))
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
    parser = OptionParser(usage='%prog [options] [sources and packages]+')

    parser.add_option('-X', '--directive', metavar='NAME=VALUE,...', dest='directives',
                      type=str, action='callback', callback=parse_directives, default={},
                      help='set a compiler directive')
    parser.add_option('-s', '--option', metavar='NAME=VALUE', dest='options',
                      type=str, action='callback', callback=parse_options, default={},
                      help='set a cythonize option')
    parser.add_option('-3', dest='python3_mode', action='store_true',
                      help='use Python 3 syntax mode by default')
    parser.add_option('-a', '--annotate', dest='annotate', action='store_true',
                      help='generate annotated HTML page for source files')

    parser.add_option('-x', '--exclude', metavar='PATTERN', dest='excludes',
                      action='append', default=[],
                      help='exclude certain file patterns from the compilation')

    parser.add_option('-b', '--build', dest='build', action='store_true',
                      help='build extension modules using distutils')
    parser.add_option('-i', '--inplace', dest='build_inplace', action='store_true',
                      help='build extension modules in place using distutils (implies -b)')
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

    options, args = parser.parse_args(args)
    if not args:
        parser.error("no source files provided")
    if options.build_inplace:
        options.build = True
    if multiprocessing is None:
        options.parallel = 0
    if options.python3_mode:
        options.options['language_level'] = 3
    return options, args


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
    start_time = datetime.now()
    print(f"START: {start_time}")

    options, paths = build_args(args)
    import pprint
    pprint.pprint(options)

    if options.annotate:  # can only be annotate or emit_linenums, not both
        Options.annotate = True

    for path in paths:
        cython_compile(path, options)
        _delete_intermediate_pdb_files(path)
        _copy_final_pdb_files(path)

    print(f"{mod_name} START TIME:   {start_time}")
    print(f"{mod_name} FINISH TIME:  {datetime.now()}")


if __name__ == '__main__':
    main()
