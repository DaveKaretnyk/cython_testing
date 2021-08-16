from ..compute_pyx_space import humanize_bytes


def test_humanize_bytes():
    assert humanize_bytes(1) == "1 byte"
    assert humanize_bytes(1024) == "1.0 kB"
    assert humanize_bytes(1024*123) == "123.0 kB"
    assert humanize_bytes(1024*12342) == "12.1 MB"
    assert humanize_bytes(1024*12342, 2) == "12.05 MB"
    assert humanize_bytes(1024*1234, 2) == "1.21 MB"
    assert humanize_bytes(1024*1234*1111, 2) == "1.31 GB"
    assert humanize_bytes(1024*1234*1111, 1) == "1.3 GB"
