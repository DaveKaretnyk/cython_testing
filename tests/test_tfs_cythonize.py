from pathlib import PurePath

from tfs_cythonize import _find_dist_base

diagnostic_print = True


def test_find_dist_base():
    some_dir = PurePath(r"C:\github\cython_testing\to_transpile2\my_utils\fei_xxx\\")
    base_dir, package_root = _find_dist_base(some_dir)
    assert base_dir == PurePath(r"C:\github\cython_testing\to_transpile2\my_utils")
    assert package_root == "fei_xxx"
    if diagnostic_print:
        print(f"checking: {some_dir}")
        print(f"    base_dir:       {base_dir}")
        print(f"        type is:    {type(base_dir)}")
        print(f"    package_root:   {type(package_root)}")
        print(f"        type is:    {package_root}")

    some_dir = PurePath(r"C:\github\cython_testing\to_transpile\fei_xxx")
    base_dir, package_root = _find_dist_base(some_dir)
    assert base_dir == PurePath(r"C:\github\cython_testing\to_transpile")
    assert package_root == "fei_xxx"
    if diagnostic_print:
        print(f"checking: {some_dir}")
        print(f"    base_dir:       {base_dir}")
        print(f"    package_root:   {package_root}")

    # Path passed does not need to exist.
    some_dir = PurePath(r"C:\a\b\c\d\fei_xxx\\")
    package_root = some_dir.stem
    base_dir = some_dir.parent
    print(f"\npackage root: {package_root}")
    print(f"base dir:     {base_dir}")
    if diagnostic_print:
        print(f"checking: {some_dir}")
        print(f"    base_dir:       {base_dir}")
        print(f"    package_root:   {package_root}")


def test_find_dist_base_autostar():
    # Somewhat redundant test, more a reminder of what that AuoStar directory structure really
    # looks like.
    autostar_dirs = [
        PurePath(r"C:\github\AUTOSTAR\ALIGNMENTS_PROTO\python\autostar_tem_sa"),
        PurePath(r"C:\github\AUTOSTAR\AutoStar\python\fei"),
        PurePath(r"C:\github\AUTOSTAR\AUTOSTAR_ALGORITHMS\python\fei_algorithms"),
        PurePath(r"C:\github\AUTOSTAR\AUTOSTAR_CALIBRATIONS\python\fei_calibrations"),
        PurePath(r"C:\github\AUTOSTAR\AUTOSTAR_COMMON\python\fei_common"),
        PurePath(r"C:\github\AUTOSTAR\AUTOSTAR_STAGE\python\fei_stage"),
        PurePath(r"C:\github\AUTOSTAR\SMART_ALIGNMENTS\python\fei_smali"),
    ]

    results = [
        (PurePath(r"C:\github\AUTOSTAR\ALIGNMENTS_PROTO\python"),       "autostar_tem_sa"),
        (PurePath(r"C:\github\AUTOSTAR\AutoStar\python"),               "fei"),
        (PurePath(r"C:\github\AUTOSTAR\AUTOSTAR_ALGORITHMS\python"),    "fei_algorithms"),
        (PurePath(r"C:\github\AUTOSTAR\AUTOSTAR_CALIBRATIONS\python"),  "fei_calibrations"),
        (PurePath(r"C:\github\AUTOSTAR\AUTOSTAR_COMMON\python"),        "fei_common"),
        (PurePath(r"C:\github\AUTOSTAR\AUTOSTAR_STAGE\python"),         "fei_stage"),
        (PurePath(r"C:\github\AUTOSTAR\SMART_ALIGNMENTS\python"),       "fei_smali"),
    ]

    for autostar_dir, result in zip(autostar_dirs, results):
        base_dir, package_root = _find_dist_base(autostar_dir)
        assert (base_dir, package_root) == result
        if diagnostic_print:
            print(f"checking: {autostar_dir}")
            print(f"    base_dir:       {base_dir}")
            print(f"    package_root:   {package_root}")
