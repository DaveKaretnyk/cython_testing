""" Re-work of Cython.Build.Cythonize.py, which implements the 'cythonize'
command line script published by the Cython package.

For AutoStar purposes there is no need to be provide such a generic API. In
fact certain compiler directives must be be precisely controlled and should
 not be changed.

Some specific reasons:
* Parallel building of Cython extensions is not supported when using setup
  'commands'. Specifically commands that are specializations of
  Cython.Distutils.build_ext.new_build_ext are not supported as commands.
* Building inplace (i.e. pyd next to the Python source) does not work when
  using 'pythons setup.py build_ext' --inplace' since this bypasses the logic
  for inplace building present in the Cython code.
* There is no need to support a 'wide range' of Python versions. E.g. AutoStar
  does not need to support earlier than 3.6.

"""

import os
import shutil
import tempfile
from pathlib import Path
from distutils.core import setup

from Cython.Build.Dependencies import cythonize, extended_iglob
from Cython.Utils import is_package_dir
from Cython.Compiler import Options

try:
    import multiprocessing
    parallel_compiles = int(multiprocessing.cpu_count() * 1.5)
except ImportError:
    multiprocessing = None
    parallel_compiles = 0


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


def find_package_base(path):
    base_dir, package_path = os.path.split(path)
    while os.path.isfile(os.path.join(base_dir, '__init__.py')):
        base_dir, parent = os.path.split(base_dir)
        package_path = '%s/%s' % (parent, package_path)
    return base_dir, package_path


def cython_compile(path_pattern, options):
    pool = None
    all_paths = map(os.path.abspath, extended_iglob(path_pattern))
    try:
        for path in all_paths:
            if options.build_inplace:
                base_dir = path
                while not os.path.isdir(base_dir) or is_package_dir(base_dir):
                    base_dir = os.path.dirname(base_dir)
            else:
                base_dir = None

            if os.path.isdir(path):
                # recursively compiling a package
                paths = [str(file_name.resolve())
                         for file_name in Path(path).rglob("*.pyx")]
            else:
                paths = [path]  # assume it's a file(-like thing)

            ext_modules = cythonize(
                paths,
                nthreads=options.parallel,
                exclude_failures=options.keep_going,
                exclude=options.excludes,
                compiler_directives=options.directives,
                force=options.force,
                quiet=options.quiet,
                **options.options)

            for ext_mod in ext_modules:
                ext_mod.libraries = ["ole32", "oleaut32", "advapi32"]
                ext_mod.extra_link_args = ["/IGNORE:4197", "-debug:full"]
                ext_mod.extra_compile_args = [
                    "-Zi",
                    f"-Fd{ext_mod.sources[0]}".replace(".c", ".pdb")]  # should only be 1 .c file

            if ext_modules and options.build:
                if len(ext_modules) > 1 and options.parallel > 1:
                    if pool is None:
                        pool = multiprocessing.Pool(options.parallel)
                    pool.map_async(run_distutils, [
                        (base_dir, [ext]) for ext in ext_modules])
                else:
                    run_distutils((base_dir, ext_modules))
    except:
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


def main(args=None):
    options, paths = build_args(args)
    import pprint
    pprint.pprint(options)

    if options.annotate:  # can only be annotate or emit_linenums, not both
        Options.annotate = True

    for path in paths:
        cython_compile(path, options)


if __name__ == '__main__':
    main()
