

# def main():
#     cythonize(
#         ["to_transpile/hello2.pyx"]
#     )

my_args = [
    # "C:/github/cython_davek/run_via_cythonize_script.py",
    "-i",
    "-a",
    "./to_transpile/hello2.pyx",
]

# if __name__ == '__main__':
#     import sys
#     from Cython.Build.Cythonize import main
#
#     sys.exit(main())

if __name__ == '__main__':
    # import sys
    from Cython.Build.Cythonize import parse_args, cython_compile
    options, paths = parse_args(my_args)

    # if options.lenient:
    #     # increase Python compatibility by ignoring compile time errors
    #     Options.error_on_unknown_names = False
    #     Options.error_on_uninitialized = False
    #
    # if options.annotate:
    #     Options.annotate = True

    for path in paths:
        cython_compile(path, options)
