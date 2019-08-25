# This code can be put in any Python module, it does not require IPython
# itself to be running already.  It only creates the magics subclass but
# doesn't instantiate it yet.
from __future__ import print_function
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
import time
import zmq
import json
import os

# The class MUST call this class decorator at creation time
# TODO: This needs to send notebook-id too.
@magics_class
class MznbMagics(Magics):

    def __init__(self, shell, port, session_id):
        # You must call the parent constructor
        super(MznbMagics, self).__init__(shell)
        self.port = port
        self.session_id = session_id

    @line_cell_magic
    def run_mzn(self, line, cell=None):
        ctx = zmq.Context()
        sock = ctx.socket(zmq.REQ)
        sock.connect('tcp://localhost:' + str(self.port))
        tic = time.time()
        request = {'action': 'execute',  # execute or show (for debugging)
                   'session-id': self.session_id,
                   'dir': os.getcwd(),
                   'cmd-line': line,
                   'body': cell}
        request_str = json.dumps(request)
        sock.send_string(request_str)
        resp = json.loads(sock.recv())
        print("Response (%.2f sec): %s " % ((time.time()-tic), resp))
