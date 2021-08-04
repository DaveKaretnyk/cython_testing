# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import filecmp
import os
import shutil
import time
import unittest

from .. import cythonize

# Explicitly list the packages to cythonize and keep them to the bare minimum needed to protect
# company sensitive material.
#
# Some packages not cythonized because they cause issues at runtime: PySide connect issue;
# function being converted to builtin_function_or_method type; trouble with Enthought traits.
#
CYTHON_INCLUDE_PACKAGES = [
    r'included_packages'
]

# Packages (directories) that should not be processed.
CYTHON_EXCLUDED_PACKAGES = [
    r'excluded_packages'
]

# Modules (files) that should not be processed.
CYTHON_EXCLUDED_MODULES = [
    r'excluded_',
]

# Items (directories and files) to exclude from the cythonized distributions.
DIST_EXCLUDED_PACKAGES = [
    '*.tests',
    '*.tests.*',
    'tests.*',
    'tests',
]


class TestCythonize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.diagnostics_print = True
        self.here = os.path.abspath(os.path.dirname(__file__))
        self.test_folder = os.path.join(self.here, "test_folder")
        self.test_source_dist = os.path.join(self.test_folder, "test_dist")
        self.test_destination_dir = "c:\\temp\\test_cythonize\\copy_test_dir"
        self._cleanup_intermediate_testfiles()

    def tearDown(self):
        self._cleanup_intermediate_testfiles()

    def _create_dummy_file(self, filepath):
        file = open(filepath, "a+")
        file.close()

    def _cleanup_intermediate_testfiles(self):
        if os.path.exists(self.test_destination_dir):
            shutil.rmtree(self.test_destination_dir)

    # Test that that _should_replace works properly
    def test_should_replace(self):
        if not os.path.exists(self.test_destination_dir):
            os.mkdir(self.test_destination_dir)

        test_source_file = os.path.join(self.test_destination_dir, "src.py")
        test_destination_file = os.path.join(self.test_destination_dir, "dst.py")

        assert not cythonize._should_replace(test_source_file, test_destination_file)

        TestCythonize._create_dummy_file(self, test_source_file)
        assert cythonize._should_replace(test_source_file, test_destination_file)
        os.unlink(test_source_file)

        TestCythonize._create_dummy_file(self, test_source_file)
        # in windows the resolution for the os.stat(src_file).st_mtime is 2 seconds so
        # if we want to check for the modification time, we need to wait 2 seconds
        time.sleep(2)
        TestCythonize._create_dummy_file(self, test_destination_file)
        assert not cythonize._should_replace(test_source_file, test_destination_file)

    # Test that that _copy_tree works properly
    def test_copy_tree(self):
        # copy a tree to a non existing one and check that the new tree is a copy of the source
        cythonize._copy_tree(self.test_source_dist, self.test_destination_dir)
        assert filecmp.dircmp(self.test_source_dist, self.test_destination_dir)

        # add a new file to and to copy tree of test_source_dist to test_destination_dist and check that
        # that test_source_dist and test_destination_dist are equal
        new_source_file = os.path.join(self.test_source_dist, "src.py")
        TestCythonize._create_dummy_file(self, new_source_file)
        new_destination_file = os.path.join(self.test_destination_dir, "src.py")
        cythonize._copy_tree(self.test_source_dist, self.test_destination_dir)
        assert filecmp.dircmp(self.test_source_dist, self.test_destination_dir)

        # change modification time of a file in test_source_dist, do the _copy_tree and check that only that file
        # as been updated in test_destination_dist)

        # in windows the resolution for the os.stat(src_file).st_mtime is 2 seconds so
        # if we want to check for the modification time, we need to wait 2 seconds
        time.sleep(2)
        os.utime(new_source_file, None)
        cythonize._copy_tree(self.test_source_dist, self.test_destination_dir)
        assert filecmp.dircmp(self.test_source_dist, self.test_destination_dir)
        assert abs(os.stat(new_source_file).st_mtime - os.stat(new_destination_file).st_mtime) < 1

        # remove new_source_file from the test_source_dist, do the _copy_tree and check that
        # that new_source_file is removed from the test_destination_dist as well
        os.unlink(new_source_file)
        cythonize._copy_tree(self.test_source_dist, self.test_destination_dir)
        assert os.path.exists(new_destination_file)

    # Test that old build folders build, dist and egginfo are removed
    def test_delete_old_build_artifacts(self):
        cythonize._copy_tree(self.test_source_dist, self.test_destination_dir)
        wheel_name = "test"
        target_directory_build = os.path.join(self.test_destination_dir, 'build')
        os.mkdir(target_directory_build)
        target_directory_dist = os.path.join(self.test_destination_dir, 'dist')
        os.mkdir(target_directory_dist)
        egg_info_filename = wheel_name + '.egg-info'
        target_directory_egg_info = os.path.join(self.test_destination_dir, egg_info_filename)
        os.mkdir(target_directory_egg_info)
        cythonize._delete_old_build_artifacts(self.test_destination_dir, wheel_name)
        assert not os.path.exists(target_directory_build)
        assert not os.path.exists(target_directory_dist)
        assert not os.path.exists(target_directory_egg_info)

    # Test that _create_pyx_file creates a new pyx file only if pyd file does not exists or is outdated
    def test_create_pyx_file(self):
        cythonize._copy_tree(self.test_source_dist, self.test_destination_dir)
        include_packages = os.path.join(self.test_destination_dir, "included_packages")
        source_folder_py_file = os.path.join(self.test_source_dist, "included_packages\\included_py_module.py")
        py_file = os.path.join(include_packages, "included_py_module.py")
        pyd_file = os.path.join(include_packages, "included_py_module.pyd")
        pyx_file = os.path.join(include_packages, "included_py_module.pyx")
        cythonize._create_pyx_file(include_packages, py_file)
        # We saw intermittent failure of this test during automated build.
        # I add here a small sleep to validate whether the issue is related to maybe some timing aspects
        # of the file system
        time.sleep(5)
        assert not os.path.exists(py_file)
        assert os.path.exists(pyx_file)

        os.unlink(pyx_file)
        shutil.copy2(source_folder_py_file, py_file)
        TestCythonize._create_dummy_file(self, pyd_file)
        cythonize._create_pyx_file(include_packages, py_file)
        time.sleep(5)
        assert not os.path.exists(py_file)
        assert not os.path.exists(pyx_file)
        assert os.path.exists(pyd_file)

        shutil.copy2(source_folder_py_file, py_file)
        time.sleep(5)
        os.utime(py_file, None)
        cythonize._create_pyx_file(include_packages, py_file)
        time.sleep(5)
        assert not os.path.exists(py_file)
        assert os.path.exists(pyx_file)
        assert not os.path.exists(pyd_file)

    # Tests that _create_new_incr_files works properly. Given the target directory, tests that all
    # distributions in dist_excluded_packages are removed, that cython_excluded_packages or 'tests'
    # or cython_excluded_modules are ignored.
    # Test that pyc and c intermediate files from previous builds are removed.
    # Test that _create_pyx_file is called.
    def test_create_new_incr_files(self):
        cythonize._copy_tree(self.test_source_dist, self.test_destination_dir)
        include_packages = os.path.join(self.test_destination_dir, "included_packages")
        pyc_file = os.path.join(include_packages, "included_py_module.pyc")
        c_file = os.path.join(include_packages, "included_py_module.c")
        pyx_file = os.path.join(include_packages, "included_py_module.pyx")
        TestCythonize._create_dummy_file(self, pyc_file)
        TestCythonize._create_dummy_file(self, c_file)
        cythonize._create_new_incr_files(self.test_destination_dir,
                                         DIST_EXCLUDED_PACKAGES,
                                         CYTHON_INCLUDE_PACKAGES,
                                         CYTHON_EXCLUDED_PACKAGES,
                                         CYTHON_EXCLUDED_PACKAGES)
        assert not os.path.exists(pyc_file)
        assert not os.path.exists(c_file)
        assert os.path.exists(pyx_file)

    # Test that that _remove_unwanted_incr_files works properly and in case of non incremental build
    # it just removes the complete folder with incremental files
    def test_remove_unwanted_incr_files(self):
        # copy a tree to a non existing one and check that the new tree is a copy of the source
        cythonize._copy_tree(self.test_source_dist, self.test_destination_dir)
        include_packages = os.path.join(self.test_destination_dir, "included_packages")
        pyd_file = os.path.join(include_packages, "included_py_module.pyd")
        TestCythonize._create_dummy_file(self, pyd_file)
        cythonize._remove_unwanted_incr_files(
            self.test_source_dist,
            self.test_destination_dir,
            DIST_EXCLUDED_PACKAGES,
            CYTHON_INCLUDE_PACKAGES,
            CYTHON_EXCLUDED_PACKAGES,
            CYTHON_EXCLUDED_PACKAGES,
            False)
        assert not os.path.exists(self.test_destination_dir)

    # Test that that _remove_unwanted_incr_files works properly and in case of incremental build
    # it leaves there only the correct ones
    def test_remove_unwanted_incr_files_incremental(self):
        # copy a tree to a non existing one and check that the new tree is a copy of the source
        cythonize._copy_tree(self.test_source_dist, self.test_destination_dir)
        include_packages = os.path.join(self.test_destination_dir, "included_packages")
        exclude_packages = os.path.join(self.test_destination_dir, "excluded_packages")
        pyd_file = os.path.join(include_packages, "included_py_module.pyd")
        TestCythonize._create_dummy_file(self, pyd_file)
        cythonize._remove_unwanted_incr_files(
            self.test_source_dist,
            self.test_destination_dir,
            DIST_EXCLUDED_PACKAGES,
            CYTHON_INCLUDE_PACKAGES,
            CYTHON_EXCLUDED_PACKAGES,
            CYTHON_EXCLUDED_MODULES,
            True)
        assert os.path.exists(self.test_destination_dir)
        assert not os.path.exists(exclude_packages)
        assert os.path.exists(include_packages)
        tests_subfolder = os.path.join(include_packages, "tests")
        assert not os.path.exists(tests_subfolder)
        listdir = os.listdir(include_packages)
        assert len(listdir) == 1
        assert os.path.exists(pyd_file)

    # Test that that _create_pyx_packages works properly for non incremental option
    def test_create_pyx_packages(self):
        dist_name = "test_dist"
        cythonize._create_pyx_packages(
            self.test_folder,
            self.test_destination_dir,
            dist_name,
            DIST_EXCLUDED_PACKAGES,
            CYTHON_INCLUDE_PACKAGES,
            CYTHON_EXCLUDED_PACKAGES,
            CYTHON_EXCLUDED_MODULES,
            False)
        test_destination_dist_path = os.path.join(self.test_destination_dir, dist_name)
        included_packages = os.path.join(test_destination_dist_path, "included_packages")
        excluded_packages = os.path.join(test_destination_dist_path, "excluded_packages")
        assert os.path.exists(included_packages)
        assert os.path.exists(excluded_packages)
        assert not os.path.exists(os.path.join(excluded_packages, "py_module.pyx"))
        assert os.path.exists(os.path.join(included_packages, "included_py_module.pyx"))
        assert not os.path.exists(os.path.join(included_packages, "excluded_py_module.pyx"))

    # Test that that _create_pyx_packages works properly with incremental option
    def test_create_pyx_packages_incremental(self):
        dist_name = "test_dist"
        cythonize._create_pyx_packages(
            self.test_folder,
            self.test_destination_dir,
            dist_name,
            DIST_EXCLUDED_PACKAGES,
            CYTHON_INCLUDE_PACKAGES,
            CYTHON_EXCLUDED_PACKAGES,
            CYTHON_EXCLUDED_MODULES,
            False)

        # validate that no included_py_module.pyx has not been created and that included_py_module.pyd
        # has not been modified
        test_destination_dist_path = os.path.join(self.test_destination_dir, dist_name)
        included_packages = os.path.join(test_destination_dist_path, "included_packages")
        pyx_file = os.path.join(included_packages, "included_py_module.pyx")
        pyd_file = os.path.join(included_packages, "included_py_module.pyd")
        assert os.path.exists(pyx_file)
        os.rename(
            pyx_file,
            pyd_file
        )
        pyd_file_mod_time = os.stat(pyd_file).st_mtime
        # st_time resolution for windows is 2 sec.
        time.sleep(1)
        cythonize._create_pyx_packages(
            self.test_folder,
            self.test_destination_dir,
            dist_name,
            DIST_EXCLUDED_PACKAGES,
            CYTHON_INCLUDE_PACKAGES,
            CYTHON_EXCLUDED_PACKAGES,
            CYTHON_EXCLUDED_MODULES,
            True)
        assert not os.path.exists(pyx_file)
        assert os.path.exists(pyd_file)
        pyd_file_mod_time_new = os.stat(pyd_file).st_mtime
        assert abs(pyd_file_mod_time_new - pyd_file_mod_time) < 1

        # simulate the situation were there is a remaining pyd from a previous cython and the corresponding
        # py file was removed. I do that by creating a new pyd in the destination folder
        pyd_file_2 = os.path.join(included_packages, "included_py_module_2.pyd")
        TestCythonize._create_dummy_file(self, pyd_file_2)
        cythonize._create_pyx_packages(
            self.test_folder,
            self.test_destination_dir,
            dist_name,
            DIST_EXCLUDED_PACKAGES,
            CYTHON_INCLUDE_PACKAGES,
            CYTHON_EXCLUDED_PACKAGES,
            CYTHON_EXCLUDED_MODULES,
            True)
        assert not os.path.exists(pyd_file_2)

        # validate that if the pyd file is older that the py file, then it will removed
        # and a new pyx file is creating instead
        py_file = os.path.join(self.test_source_dist, "included_packages\\included_py_module.py")
        py_file_time = os.stat(py_file).st_mtime
        new_mod_time = py_file_time - 120
        os.utime(pyd_file, (new_mod_time, new_mod_time))
        cythonize._create_pyx_packages(
            self.test_folder,
            self.test_destination_dir,
            dist_name,
            DIST_EXCLUDED_PACKAGES,
            CYTHON_INCLUDE_PACKAGES,
            CYTHON_EXCLUDED_PACKAGES,
            CYTHON_EXCLUDED_MODULES,
            True)
        assert not os.path.exists(pyd_file)
        assert os.path.exists(pyx_file)

    # Test that that _collect_extensions works properly
    def test_collect_extensions(self):
        dist_name = "test_dist"
        cythonize._create_pyx_packages(
            self.test_folder,
            self.test_destination_dir,
            dist_name,
            DIST_EXCLUDED_PACKAGES,
            CYTHON_INCLUDE_PACKAGES,
            CYTHON_EXCLUDED_PACKAGES,
            CYTHON_EXCLUDED_MODULES,
            False)
        extensions = cythonize._collect_extensions(self.test_destination_dir)
        assert len(extensions) == 1

    # TODO: Find out a way to unit test 'python setup.py cythonize' and 'python setup.py cythonize_incremental'
