TEM s/w RawImage get_data
=========================

**Description**
Issue at runtime when using RawImage:
    '_get_data() takes exactly one argument (0 given)'
Maybe it's due to the fact that C does not support defaults?

This issue was only seen in the 'early days of AutoStar' where the comtraits /
comtypes interop layer was used to bind to the TEM imaging software RawImage
COM object.

Not really a problem anymore since AutoStar uses TEM_OMP and Boost Python (or
pybind11) to convert data to something more 'Python friendly'.

**Solutions / Workarounds**
None.

More information:
None.
