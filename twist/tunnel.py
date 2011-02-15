#
# Copyright (c) 2008, Technische Universitaet Berlin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# - Neither the name of the Technische Universitaet Berlin nor the names
#   of its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Author: Andreas Koepke (koepke at tkn.tu-berlin.de)

import os
import sys

from twisted.application import service
from twisted.internet import reactor, error
from twisted.protocols.portforward import ProxyFactory
from twisted.python import log, util as tutil

from store import TwistStore

import ConfigParser

config=ConfigParser.SafeConfigParser()
config.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

sfoffset = config.getint('supernode', 'sfoffset')
ipoffset = config.getint('supernode', 'ipoffset')
ipprefix = config.getint('supernode', 'ipprefix')


class TunnelService(service.Service):
    
    def __init__(self):
        self.store = TwistStore()

    def startService(self):
        self.running = 1
        self.fireTunnels()
        
    def fireTunnels(self):
        def _cb(result):
            for tup in result:
                port = sfoffset+tup['node_id']
                ip   = ipoffset+tup['supernode_id']
                try:
                    reactor.listenTCP(port, ProxyFactory("192.168.1." + str(ip), port))
                except error.CannotListenError:
                    log.err("Can not Listen: " + str(port) + " 192.168.1." + str(ip))
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err(msg)
        

        self.store.getAllNodeSupernodeBindingRecords().addCallbacks(_cb, _eb)

def createTunnels():
    ts=TunnelService()
    return ts
    
if __name__ == "__main__":
    
    log.startLogging(sys.stdout)
    
    reactor.callWhenRunning(createTunnels)
    reactor.run()
