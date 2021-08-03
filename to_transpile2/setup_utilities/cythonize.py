# Copyright (c) 2018-2020 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
""" Code for cythonizing, including incrementally, a source tree.

    Requirements: Microsoft Visual C++ Compiler 15.0 or later installed and configured.
    See '.../AUTOSTAR/build/Build-PythonWheel/Set-DevEnv'.
"""
import os
import zipfile
from os import path
import shutil
import glob
import stat
import time
import datetime
from setuptools import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext


def _should_replace(src_file, dst_file):
    """ Returns if src_file should replace destination file"""

    if not os.path.exists(src_file):
        return False

    if not os.path.exists(dst_file):
        return True

    return os.stat(src_file).st_mtime >= (os.stat(dst_file).st_mtime + 1)


def _copy_tree(src, dst, symlinks=False, ignore=None):
    """ Copy a tree updating only more recent files"""
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except Exception:
                pass  # lchmod not available
        elif os.path.isdir(s):
            _copy_tree(s, d, symlinks, ignore)
        elif _should_replace(s, d):
            shutil.copy2(s, d)


def _leave_only_pyd_files(cython_excluded_modules, cython_excluded_packages,
                          cython_include_packages, dist_excluded_packages, target_directory):
    """ Remove all intermediate files except the pyd files """

    for _path, dirnames, filenames in os.walk(target_directory):

        # packages that are excluded from the dist should be removed
        # it could happen that a dist has been added to the dist_excluded_packages
        # after last cythonization
        if any(package in _path for package in dist_excluded_packages):
            shutil.rmtree(_path)
            continue

        # packages that are excluded from cythonization should be removed
        # it could happen that a package has been added to the cython_excluded_packages
        # after last cythonization
        if any(package in _path for package in cython_excluded_packages) or "tests" in _path:
            shutil.rmtree(_path)
            continue

        if any(package in _path for package in cython_include_packages):

            for filename in filenames:
                filepath = os.path.join(_path, filename)

                # modules that are excluded from cythonization should be removed
                # it could happen that a module has been added to the cython_excluded_modules
                # after last cythonization
                if any(module in filename for module in cython_excluded_modules):
                    os.unlink(filepath)
                    continue

                root, ext = os.path.splitext(filename)

                # remove non pyd files
                if ext != '.pyd':
                    os.unlink(filepath)
                    continue


def _remove_outdated_pyd_files(cython_include_packages, source_directory, target_directory):
    """ Remove all pyd files that are outdated because the corresponding py file does not longer
    exists """

    # now only pyd file that were caused by previous cythonization are left
    # let's remove the one that do not have a .py file counter part in the source directory
    # as this means that that .py file has been removed or renamed after last cythonization
    for _path, dirnames, filenames in os.walk(target_directory):

        if any(package in _path for package in cython_include_packages):

            for filename in filenames:
                filepath = os.path.join(_path, filename)

                root, ext = os.path.splitext(filename)

                py_file = os.path.join(_path, '{}{}'.format(root, '.py'))

                relative_path_target_file = os.path.relpath(py_file, target_directory)
                source_path_target_file = os.path.join(source_directory, relative_path_target_file)

                # if we have a file, and no py file with same name is present in the source path
                # then that py file has been removed lately, so we remove this file in the
                # target path as well
                if not os.path.exists(source_path_target_file):
                    os.unlink(filepath)
                    continue


def _remove_unwanted_incr_files(source_directory,
                                target_directory,
                                dist_excluded_packages,
                                cython_include_packages,
                                cython_excluded_packages,
                                cython_excluded_modules,
                                incremental):
    """ Remove all unwanted incremental files from the target directory that are related to
    removed files.

    Only for pyd we need to check if we want to remove them or not pyd files. It depends whether
    the related py file was removed after last build or not.
    """

    if not incremental:
        # delete target directory
        if os.path.exists(target_directory):
            os.system('rmdir /S /Q \"{}\"'.format(target_directory))
    else:
        _leave_only_pyd_files(cython_excluded_modules, cython_excluded_packages,
                              cython_include_packages, dist_excluded_packages, target_directory)

        _remove_outdated_pyd_files(cython_include_packages, source_directory, target_directory)


def _delete_old_build_artifacts(target_directory, wheel_name):
    target_directory_build = os.path.join(target_directory, 'build')
    if os.path.exists(target_directory_build):
        os.system('rmdir /S /Q \"{}\"'.format(target_directory_build))
    target_directory_dist = os.path.join(target_directory, 'dist')
    if os.path.exists(target_directory_dist):
        os.system('rmdir /S /Q \"{}\"'.format(target_directory_dist))
    egg_info_filename = wheel_name + '.egg-info'
    target_directory_egg_info = os.path.join(target_directory, egg_info_filename)
    if os.path.exists(target_directory_egg_info):
        os.system('rmdir /S /Q \"{}\"'.format(target_directory_egg_info))


def _create_pyx_file(path, filename):
    # if pyd file is older, then we remove it and create the pyx file so that
    # it will be cythonized

    py_file = os.path.join(path, filename)
    root, ext = os.path.splitext(filename)
    pyd_file = os.path.join(path, '{}{}'.format(root, '.pyd'))

    if _should_replace(py_file, pyd_file):
        print("new file to cythonize: {0}".format(py_file))
        # remove the pyd
        if os.path.exists(pyd_file):
            os.unlink(pyd_file)
        target_file = os.path.join(path, '{}{}'.format(root, '.pyx'))
        # remove the previous pyx file
        if os.path.exists(target_file):
            os.unlink(target_file)
        os.rename(
            py_file,
            target_file
        )
    else:
        target_file = os.path.join(path, '{}{}'.format(root, '.pyx'))
        # remove the previous pyx file
        if os.path.exists(target_file):
            os.unlink(target_file)
        # remove the .py file
        os.unlink(py_file)


def _create_new_incr_files(target_directory_fei,
                           dist_excluded_packages,
                           cython_include_packages,
                           cython_excluded_packages,
                           cython_excluded_modules):
    """Iterates throw the target directory and clean up the old unwanted incremental files
    and create the new pyx files"""
    for _path, dirnames, filenames in os.walk(target_directory_fei):

        if any(package in _path for package in dist_excluded_packages):
            shutil.rmtree(_path)
            continue

        if any(package in _path for package in cython_include_packages):

            if any(package in _path for package in cython_excluded_packages) or "tests" in _path:
                continue

            for filename in filenames:

                if any(module in filename for module in cython_excluded_modules):
                    continue

                filepath = os.path.join(_path, filename)

                root, ext = os.path.splitext(filename)

                # remove pyc files
                if ext == '.pyc':
                    os.unlink(filepath)
                    continue

                # remove c files
                if ext == '.c':
                    os.unlink(filepath)
                    continue

                # skip all the non python files
                if ext != '.py':
                    continue

                # don't cythonize setup.py and __init__.py
                if root in ['setup', '__init__']:
                    continue

                _create_pyx_file(_path, filename)


def _create_pyx_packages(source_directory,
                         target_directory,
                         dist_root_name,
                         dist_excluded_packages,
                         cython_include_packages,
                         cython_excluded_packages,
                         cython_excluded_modules,
                         incremental=False):
    """ Copies all the selected packages to cythonize into the target
    directory and rename py files to pyx.
    If incremental option is selected then only changed py files will be
    cythonized.
    """

    source_directory_fei = os.path.join(source_directory, dist_root_name)
    target_directory_fei = os.path.join(target_directory, dist_root_name)

    _remove_unwanted_incr_files(
        source_directory_fei,
        target_directory_fei,
        dist_excluded_packages,
        cython_include_packages,
        cython_excluded_packages,
        cython_excluded_modules,
        incremental
    )

    _copy_tree(source_directory_fei, target_directory_fei,
               ignore=(shutil.ignore_patterns(*dist_excluded_packages)))

    setup_file_path = os.path.join(source_directory, 'setup.py')
    shutil.copy2(setup_file_path, target_directory)

    _create_new_incr_files(target_directory_fei,
                           dist_excluded_packages,
                           cython_include_packages,
                           cython_excluded_packages,
                           cython_excluded_modules)


def _create_debug_symbols_zip(relative_dir):
    zip_file_name = f'{relative_dir}_dbg_symbols.zip'
    full_dir = path.join(os.getcwd(), relative_dir)
    file_types = ['.pyx', '.c', '.pdb']  # only dirs with these file types

    print(f'archive dbg symbols for dir {full_dir} to {zip_file_name}')
    print(f'    only these file types: {file_types}')

    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(relative_dir):
            for file in files:
                if file.endswith(tuple(file_types)):
                    zip_file.write(os.path.join(root, file))


def _collect_extensions(from_directory):
    """ Collect build extensions. """

    cython_extension_directories = []
    for dirpath, directories, files in os.walk(from_directory):
        # if the directory contains pyx files, cythonize it
        if len(glob.glob('{0}/*.pyx'.format(dirpath))) > 0:
            cython_extension_directories.append(dirpath)

    collected_extensions = cythonize(
        [
            Extension(
                '*',
                ['{}/*.pyx'.format(dirpath)],
                libraries=['ole32', 'oleaut32', 'advapi32'],

                # 'Od': disable optimizations, 'Zi': generate full debug info.
                extra_compile_args=["-Zi", "-Od"],

                # /IGNORE:4197: suppress warning of function declared for export more than once
                # -debug=full: use debug info to create pdb files
                extra_link_args=['/IGNORE:4197', '-debug:full'],

            ) for dirpath in cython_extension_directories
        ],
        # Set language level to 3.X, else prints with keyword parameters do not compile.
        compiler_directives={'language_level': '3'},

        # add #line directives throughout the generated C/C++ code, 'semi-secret option' that
        # allows symbol mapping back to .pyx Python source. Cannot be used with with 'annotate'
        # option!
        emit_linenums=True,
    )

    return collected_extensions


def _remove_items(target_directory, exclude_list):
    """ Remove specified items from the target directory """

    print("\nRemove specified items from: ", target_directory)
    for _path, dirnames, filenames in os.walk(target_directory):

        if any(dir in _path for dir in exclude_list):
            shutil.rmtree(_path)
            # added because Windows OS delete is not synchronous
            # intermittent issues observed in the past
            time.sleep(0.05)
            continue

        for filename in filenames:
            file_path = os.path.join(_path, filename)
            for substring in exclude_list:
                if substring in file_path:
                    os.remove(file_path)
                    continue


def _get_first_subdir(target_directory, name):
    """ Return the first occurrence of a subdirectory containing the specified name """
    for _path, dirnames, filenames in os.walk(target_directory):
        for dirname in dirnames:
            if name in dirname:
                return os.path.join(_path, dirname)


def build_cython_packages(self,
                          root,
                          wheel_name,
                          dist_root_name,
                          dist_excluded_packages,
                          cython_include_packages,
                          cython_excluded_packages,
                          cython_excluded_modules,
                          incremental=False,
                          dist_excluded_items=None):
    """ Build the python packages. """

    start_build_cython_packages = time.time()

    print("\nBuild_cython_packages")
    cython_directory = os.path.join(root, 'cythonized')
    fei_directory = os.path.join(cython_directory, dist_root_name)
    old_inplace = self.inplace

    build_temp = os.path.abspath(os.path.join(root, "..\\..\\" + self.build_temp))
    self.build_temp = build_temp

    print("TARGET_DIR: " + cython_directory)
    print("Temp build folder for cythonization: " + self.build_temp)
    print("")

    _delete_old_build_artifacts(cython_directory, wheel_name)

    # if a test wheel command was ran before remove the tests from it
    if os.path.exists(cython_directory) and os.path.exists(fei_directory) \
            and _get_first_subdir(fei_directory, 'tests'):
        _remove_items(os.path.join(cython_directory, dist_root_name), dist_excluded_items)
        os.chdir(cython_directory)
        print("\nCreate wheel from previously ran test wheel command")
        print("")
    else:
        # otherwise call regular transpile methods
        _create_pyx_packages(root,
                             cython_directory,
                             dist_root_name,
                             dist_excluded_packages,
                             cython_include_packages,
                             cython_excluded_packages,
                             cython_excluded_modules,
                             incremental)

        print("\ncollect_extensions")
        print("")
        self.extensions = _collect_extensions(cython_directory)

        print("\nbuild_ext.run(self)")
        print("")
        os.chdir(cython_directory)
        old_inplace = self.inplace
        self.inplace = 1
        build_ext.run(self)

    print("\nCreate wheel")
    print("")
    os.system('python setup.py bdist_wheel')  # TODO??? check exit code!

    if os.path.exists(build_temp):
        msg = "\nGet rid of the temporary build folder: path too long path,"
        msg += " creates issues when copying to the holding area"
        print(msg)
        print("")
        os.system('rmdir /S /Q \"{}\"'.format(build_temp))

    self.inplace = old_inplace

    end_build_cython_packages = time.time()
    time_spent = end_build_cython_packages - start_build_cython_packages
    d = datetime.timedelta(seconds=time_spent)

    _create_debug_symbols_zip(path.basename(path.normpath(dist_root_name)))

    print("\nBuild_cython_packages done. Time Elapsed: ", d)

    os.chdir(root)

