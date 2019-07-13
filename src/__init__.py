from __future__ import absolute_import
from .mznb import MznbMagics

from os import path

def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.    
    ipython.register_magics(MznbMagics)
