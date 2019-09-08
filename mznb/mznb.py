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
import uuid

# The class MUST call this class decorator at creation time
@magics_class
class MznbMagics(Magics):

    def __init__(self, shell, port, session_id):
        # You must call the parent constructor
        super(MznbMagics, self).__init__(shell)
        self.port = port
        self.endpoint = 'tcp://localhost:' + str(self.port)
        self.session_id = session_id
        self.trans_id = None
        self.sock = None # We thread this thru the different magic functions.

    @line_cell_magic
    def preprocess_mzn(self, line, cell=None):
        self.trans_id = str(uuid.uuid1())
        ctx = zmq.Context()
        self.sock = ctx.socket(zmq.REQ)
        self.sock.connect(self.endpoint)
        request = {'action': 'pre-process', 
                   'session-id': self.session_id,
                   'trans-id': self.trans_id, 
                   'nb-dir': os.getcwd(),
                   'cmd-line': '--print-vars', # POD fix me.
                   'body': cell}
        self.sock.send_string(json.dumps(request))

    @line_magic
    def run_mzn(self, line, cell=None, body=None):
        print(json.loads(self.sock.recv()))
        self.sock.disconnect(self.endpoint)
        
        ctx = zmq.Context()
        self.sock = ctx.socket(zmq.REQ)
        self.sock.connect(self.endpoint)
        request = {'action': 'execute', 
                   'session-id': self.session_id,
                   'trans-id': self.trans_id}
        self.sock.send_string(json.dumps(request))
        print(json.loads(self.sock.recv()))   # Block!
        self.sock.disconnect(self.endpoint)

    @line_magic
    def postprocess_mzn(self, line):
        ctx = zmq.Context()
        self.sock = ctx.socket(zmq.REQ)
        self.sock.connect(self.endpoint)
        request = {'action': 'post-process', 
                   'session-id': self.session_id,
                   'trans-id': self.trans_id}
        self.sock.send_string(json.dumps(request))

    @line_magic
    def cleanup_mzn(self, line):
        print(json.loads(self.sock.recv())) 
        self.sock.disconnect(self.endpoint)


