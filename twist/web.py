#!/usr/bin/env python
#
# Copyright (c) 2007, Technische Universitaet Berlin
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
# Author: Vlado Handziski (handzisk at tkn.tu-berlin.de)

import sys

from twisted.application import internet
from twisted.internet import task, reactor, ssl, protocol
from twisted.python import log, util as tutil
from twisted.cred import portal, checkers, credentials

from nevow import appserver

from store import TwistStore
from tracestore import TwistTraceStore
from poestore import TwistPoeStore
from textcha import TwistTextCha

from auth import TwistRealm, TwistChecker, TwistMind, TwistSessionWrapper

from twist_xmlrpc_api import TWIST_XMLRPC_Factory, TWIST_XMLRPC_API

def wrapAuthorized():
    store = TwistStore()
    job_archiver = task.LoopingCall(store.refreshAllArchivedJobRecords)
    job_archiver.start(300, True)
    # trace_store=TwistTraceStore()
    trace_store=object()
    # poe_store=TwistPoeStore()
    poe_store=object()
    textcha=TwistTextCha()
    realmObject = TwistRealm(store, trace_store, poe_store, textcha)
    portalObject = portal.Portal(realmObject)
    twistChecker = TwistChecker(store)
    portalObject.registerChecker(checkers.AllowAnonymousAccess(), credentials.IAnonymous)
    portalObject.registerChecker(twistChecker)
    site = appserver.NevowSite(resource=TwistSessionWrapper(portalObject, mindFactory=TwistMind))
    
    # TWIST_XMLRPC_API
    xmlrpc_resource = TWIST_XMLRPC_API(portalObject)
    xmlrpc_factory = TWIST_XMLRPC_Factory(xmlrpc_resource)
    
    return site, xmlrpc_factory

def createAuthorized(doSSL = True, port=8000, xmlrpc_port=8001):
    site, xmlrpc_factory = wrapAuthorized()

    if doSSL:
        sslContext = ssl.DefaultOpenSSLContextFactory(
            tutil.sibpath(__file__, 'cert/privkey.pem'),
            tutil.sibpath(__file__, 'cert/cacert.pem')
        )

        serve = internet.SSLServer(
            port,
            site,
            contextFactory = sslContext
        )

    else:
        serve = internet.TCPServer(
            port,
            site,
        )
        
    # TWIST_XMLRPC_API
    xmlrpc_service = internet.TCPServer(xmlrpc_port, xmlrpc_factory)     
    
    return serve, xmlrpc_service

def startAuthorized():
    
    serve, xmlrpc_service = createAuthorized(False, port=8002, xmlrpc_port=8001)
    serve.startService()
    
    # TWIST_XMLRPC_API
    xmlrpc_service.startService()
    
if __name__ == "__main__":
    
    log.startLogging(sys.stdout)
    reactor.callWhenRunning(startAuthorized)
    reactor.run()
