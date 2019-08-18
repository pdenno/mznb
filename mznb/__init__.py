from __future__ import absolute_import
from .mznb import MznbMagics
import json
from pathlib import Path
import os
import zmq
from ipykernel import get_connection_file

import urllib.request
from notebook import notebookapp


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.

    # https://gist.github.com/mbdevpl/f97205b73610dd30254652e7817f99cb
    connection_file_path = get_connection_file()
    connection_file = os.path.basename(connection_file_path)
    kernel_id = connection_file.split('-', 1)[1].split('.')[0]

    ipynb_filename = 'unknown'
    last_active = 'unknown'
    servers = list(notebookapp.list_running_servers())
    for svr in servers:
        response = urllib.request.urlopen('http://127.0.0.1:8888/api/sessions?token=' + svr['token'])
        sessions = json.loads(response.read().decode())
        for sess in sessions:
            if sess['kernel']['id'] == kernel_id:
                ipynb_filename = (sess['notebook']['path'])
                last_active = (sess['kernel']['last_activity'])
                break

    config_file = str(Path.home()) + "/.local/share/nb-agent/runtime.json"
    with open(config_file) as json_file:
        data = json.load(json_file)
        port = data['magic-server-port']

    ctx = zmq.Context()
    sock = ctx.socket(zmq.REQ)
    sock.connect('tcp://localhost:' + str(port))
    try:
        short_name = ipython.user_ns['notebook_id']
        msg = {'action': 'notify',
               'dir': os.getcwd(),
               'ipynb-file': ipynb_filename,
               'last-active': last_active,
               'connection-file': connection_file_path,
               'short-name': short_name}
        msg_str = json.dumps(msg)
        sock.send_string(msg_str)
        print('MiniZinc Notebook Agent Communicator version', __version__,
              'connected to nb-agent at port', str(port))
        sock.close()
        ctx.term()  # https://github.com/zeromq/pyzmq/issues/831
    except KeyError:
        print('''Not able to communicate with nb-agent.''')

    magics = MznbMagics(ipython, port)
    ipython.register_magics(magics)


__version__ = '0.1.dev'
