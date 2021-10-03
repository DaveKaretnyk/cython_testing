Call stack use
==============

**Description**
E.g. AutoStar Mono / OptiMono simulation utility code: walks the Python call
stack so does not work as complied C code.

Python code runs OK.

The Cython code compiles and runs but stack frame is obviously very different.
Previously (under Python 2.7.X and older Cython version) code like this caused
an exception (do no recall the details), now OK under Python 3.6.X and newer
Cython version (0.28.5).

So status not clear: more investigation if code like this is needed - maybe
not so likely for production code.

More information:
See example, running the Python code gives:
    frame_info: is_auto_sim_control_app
    frame_info: get_aaa
    frame_info: get_aa
    frame_info: get_a
    frame_info: <module>
    result is: 7

See example, running the Cython code gives:
    frame_info: <module>
    result is: 7
