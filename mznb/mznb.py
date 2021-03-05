# This code can be put in any Python module, it does not require IPython
# itself to be running already.  It only creates the magics subclass but
# doesn't instantiate it yet.
from __future__ import print_function
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
import zmq
import zmq.asyncio
import json
import asyncio
import datetime as dt

# The class MUST call this class decorator at creation time
@magics_class
class MznbMagics(Magics):

    def __init__(self, shell, port, session_id):
        # You must call the parent constructor
        super(MznbMagics, self).__init__(shell)
        self.port = port
        self.endpoint = 'tcp://localhost:' + str(self.port)
        self.context = zmq.asyncio.Context()
        self.session_id = session_id
        self.trans_id = None
        self.sock = None  # We thread this thru the different magic functions.
        self.still_waiting = True
        shell.push({'mznb_magic': self})

    async def listen(self):
        print('Awaiting result {0}'.format(dt.datetime.now()))
        while self.still_waiting:
            try:
                msg = await self.sock.recv()
                msg = json.loads(msg)
            except zmq.ZMQError:
                msg = False
            if msg:
                print('Finished        {0}'.format(dt.datetime.now()))
                print(msg)
                self.still_waiting = False

    async def start_listening(self):
        task = asyncio.create_task(self.listen())
        await task

    @cell_magic
    def run_mzn(self, line, cell=None):
        self.still_waiting = True
        self.sock = self.context.socket(zmq.REQ)
        self.sock.connect(self.endpoint)
        request = {'action': 'execute',
                   'session-id': self.session_id,
                   'cmd-line': line,
                   'body': cell}
        self.sock.send_string(json.dumps(request))
        print('Cell sent to the Notebook Agent for a MiniZinc solution.')

    @line_magic
    def run_mzn_again(self, line, cell=None):
        self.still_waiting = True
        self.sock = self.context.socket(zmq.REQ)
        self.sock.connect(self.endpoint)
        request = {'action': 'execute_again',
                   'session-id': self.session_id,
                   'cmd-line': line}
        self.sock.send_string(json.dumps(request))
        print('Executing MiniZinc again using new data.')
