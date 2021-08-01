import sys
import argparse
from pathlib import Path
""" Calculate the total size of all the .pyx files in the directory supplied.
"""


def humanize_bytes(num_bytes, precision=1):
    """Return a humanized string representation of a number of bytes.

    Examples:
    >>> humanize_bytes(1)
    '1 byte'
    >>> humanize_bytes(1024)
    '1.0 kB'
    >>> humanize_bytes(1024*123)
    '123.0 kB'
    >>> humanize_bytes(1024*12342)
    '12.1 MB'
    >>> humanize_bytes(1024*12342,2)
    '12.05 MB'
    >>> humanize_bytes(1024*1234,2)
    '1.21 MB'
    >>> humanize_bytes(1024*1234*1111,2)
    '1.31 GB'
    >>> humanize_bytes(1024*1234*1111,1)
    '1.3 GB'
    """
    abbrevs = (
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'kB'),
        (1, 'bytes')
    )
    factor, suffix = 1, "byte"
    if num_bytes == 1:
        return f"{factor} {suffix}"
    for factor, suffix in abbrevs:
        if num_bytes >= factor:
            break
    return '%.*f %s' % (precision, num_bytes / factor, suffix)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--directory", required=True)
    my_args = arg_parser.parse_args()
    print(f"processing directory : {my_args.directory}")
    target_dir = Path(my_args.directory)

    files = [f for f in target_dir.rglob("*.pyx")]
    total_size = 0
    for f in files:
        size = f.stat().st_size
        total_size += size
        print(f"{humanize_bytes(size)}    {f.absolute()}")
    print(f"total number of  .pyx files:       {len(files)}")
    print(f"total size occupied by .pyx files: {humanize_bytes(total_size)}")


if __name__ == '__main__':
    sys.exit(main())
