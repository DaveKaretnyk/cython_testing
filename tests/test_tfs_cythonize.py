
from tfs_cythonize import find_dist_base

diagnostic_print = True


def test_find_dist_base():
    some_dir = r"C:\github\cython_testing\to_transpile2\my_utils\fei_xxx\\"
    base_dir, package_root = find_dist_base(some_dir)
    assert base_dir == r"C:\github\cython_testing\to_transpile2\my_utils"
    assert package_root == "fei_xxx"

    if diagnostic_print:
        print(f"checking: {some_dir}")
        print(f"    base_dir:       {base_dir}")
        print(f"    package_root:   {package_root}")

    some_dir = r"C:\github\cython_testing\to_transpile\fei_xxx"
    base_dir, package_root = find_dist_base(some_dir)
    assert base_dir == r"C:\github\cython_testing\to_transpile"
    assert package_root == "fei_xxx"

    if diagnostic_print:
        print(f"checking: {some_dir}")
        print(f"    base_dir:       {base_dir}")
        print(f"    package_root:   {package_root}")
