# This code can be put in any Python module, it does not require IPython
# itself to be running already.  It only creates the magics subclass but
# doesn't instantiate it yet.
from __future__ import print_function
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
import time
import zmq

# The class MUST call this class decorator at creation time
@magics_class
class MznbMagics(Magics):

    def __init__(self, shell, data):
        # You must call the parent constructor
        super(MznbMagics, self).__init__(shell)
        self.data = data    

    @line_cell_magic
    def run_mzn(self, line, cell=None):
        ctx = zmq.Context()
        req = ctx.socket(zmq.REQ)
        req.connect('tcp://localhost:3178')
        tic = time.time()
        request = "%%run_mzn " + line + cell
        req.send_string(request)
        resp = req.recv()
        print("%s: %.2f ms" % (resp, 1000*(time.time()-tic)))

