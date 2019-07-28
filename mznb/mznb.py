# This code can be put in any Python module, it does not require IPython
# itself to be running already.  It only creates the magics subclass but
# doesn't instantiate it yet.
from __future__ import print_function
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
import time
import zmq
import json

# The class MUST call this class decorator at creation time
# TODO: This needs to send notebook-id too. 
@magics_class
class MznbMagics(Magics):

    def __init__(self, shell, port):
        # You must call the parent constructor
        super(MznbMagics, self).__init__(shell)
        self.port = port
        
    @line_cell_magic
    def run_mzn(self, line, cell=None):
        ctx = zmq.Context()
        sock = ctx.socket(zmq.REQ)
        sock.connect('tcp://localhost:' + str(self.port))
        tic = time.time()
        try:
            nb_id = self.shell.user_ns['notebook_id']
            line_plus = line + ' --short-name ' + nb_id
            request = {'action' : 'execute',
                       'cmd-line' : line_plus,
                       'body' : cell}
            request_str = json.dumps(request)
            sock.send_string(request_str)
            resp =  sock.recv()
            print("%s %s: %.2f ms" % (self.port, resp, 1000*(time.time()-tic)))
        except KeyError:
            print('''Please specify "notebook_id = {'short_name' : <whatever you'd like>}', prior to running this cell.''')

