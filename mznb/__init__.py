from __future__ import absolute_import
from .mznb import MznbMagics
#import pyzmq as zmq

def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    print('MiniZinc Notebook Agent Communicator version', __version__)
    magics = MznbMagics(ipython, 'foo') 
    ipython.register_magics(magics)

__version__ = '0.1.dev'    
