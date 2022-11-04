Use of GenericMeta
==================

**Description**
I.e. changes needed to run Python code since 'GenericMeta' is no longer available. See PEP 560:
https://peps.python.org/pep-0560/

* Modified Python code runs OK un 3.10.4.
* 3.6 code looks are little overcomplicated anyway? I.e. why was metaclass used at all?
* 3.6.0 version - see files ending '_360.py'.

* To run the 3.6.0 code an edm environment needs to be used.
* 3.6.0 is not available via conda (main channel or even conda-forge channel). And the numpy
  version for 3.6.0 coming from conda-forge and does not work properly.

So not a Cython specific problem actually.

