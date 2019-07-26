from __future__ import absolute_import
from .mznb import MznbMagics
import json
from pathlib import Path


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    config_file = str(Path.home()) + "/.local/share/nb-agent/runtime.json"
    with open(config_file) as json_file:
        data = json.load(json_file)
        port = data['magic-server-port']

    print('MiniZinc Notebook Agent Communicator version', __version__, 'connected at', port)
    magics = MznbMagics(ipython, port) 
    ipython.register_magics(magics)

__version__ = '0.1.dev'    
