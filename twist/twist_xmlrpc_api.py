#!/usr/bin/env python
#
# Copyright (c) 2010, Technische Universitaet Berlin
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
# Author: Claudio Donzelli (claudio.donzelli at tu-berlin.de)

import xmlrpclib

from twisted.web import server, xmlrpc, http
from datetime import datetime
from twisted.internet import defer
from twisted.cred import credentials

from auth import IXMLRPCAvatar
from user import TwistUser

from twisted.python import failure, log
from twisted.cred import error as credError

class TWIST_XMLRPC_Factory(server.Site):
    def __init__(self, resource):
        server.Site.__init__(self, resource)

class TWIST_XMLRPC_API(xmlrpc.XMLRPC):
    def __init__(self, portal):
        xmlrpc.XMLRPC.__init__(self)
        self.portal = portal
    
    # XMLRPC TEST
    def xmlrpc_now(self):
        return datetime.now()
    
    # LIST OF EXPORTED FUNCTIONS (XMLRPC SKELETON)
    def xmlrpc_getAllJobs(self):
        def _cb(r):
            return map(dict, r)
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err(msg)
            return []
        d=self.user.getAllJobs()
        d.addCallbacks(_cb, _eb)
        return d

    def render(self, request):
        username = request.getUser()
        password = request.getPassword()    
        creds = credentials.UsernamePassword(username, password)
        d = self.portal.login(creds, None, IXMLRPCAvatar)
        d.addCallback(self._loginSucceeded, request)
        d.addErrback(self._loginFailed, request)
        return server.NOT_DONE_YET
        
    def _loginSucceeded(self, avatarInfo, request):
        avatarInterface, avatar, logout = avatarInfo
        self.user = avatar.user
        self.render_POST(request)
        
    def _loginFailed(self, login_failure, request):
        msg=login_failure.getErrorMessage().strip()
        log.err(msg)
        request.setResponseCode(http.UNAUTHORIZED)
        request.finish()
                                     
            

        