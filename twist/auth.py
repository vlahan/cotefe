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


import os
import sha
import base64

import ConfigParser

from zope.interface import implements, Interface

from twisted.internet import defer
from twisted.python import log, failure, util as tutil
from twisted.cred import portal, checkers, credentials, error as credError
from nevow import inevow, url
from nevow.guard import SessionWrapper, urlToChild

from user import TwistUser

from page.main import WelcomePage, LoggedInPage

config=ConfigParser.SafeConfigParser()

config.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

def passwd_encode(passwd):
    return base64.b64encode("twistSlT$"+ sha.new("twistSlT$%s" % passwd).digest())

def noLogout(*args, **named):
    return None

class IXMLRPCAvatar(Interface):
    "should have attributes username and password"

class XMLRPCAvatar:
    implements(IXMLRPCAvatar)
    def __init__(self, user):
        self.user = user
        
users = {}
    
class TwistChecker(object):
    
    implements(checkers.ICredentialsChecker)
    
    credentialInterfaces = (credentials.IUsernamePassword,)
    
    def __init__(self, store=None):
        self.store=store


    def requestAvatarId(self, credentials):
        # this checks the user dictionary cache for entries matching the provided username and password
        if users.has_key(credentials.username):
            if users[credentials.username] == passwd_encode(credentials.password):
                return defer.succeed(credentials.username)
        else:
            d=self.store.getUserCredentials(credentials.username)
            d.addCallback(self._cbGetUserCredentials, credentials)
            d.addErrback(self._ebGetUserCredentials)
            return d

    def _cbGetUserCredentials(self, kwr, credentials):
        if kwr:
            dbuser=kwr[0]
            if dbuser['passwd_hash']==passwd_encode(credentials.password):
                if dbuser['enabled'] and dbuser['role']!='requested':
                    users[dbuser['username']] = dbuser['passwd_hash'] # update the user dictionary cache
                    return defer.succeed(dbuser['username'])
                elif not dbuser['enabled'] and dbuser['role']=='requested':
                    raise credError.UnauthorizedLogin('Checker:Account is not yet authorized.')
            raise failure.Failure(credError.UnauthorizedLogin('Checker:Username and password do not match.'))

        else:
            raise failure.Failure(credError.UnauthorizedLogin('Checker:Username and password do not match.'))
                
    def _ebGetUserCredentials(self, f):
        msg=f.getErrorMessage().strip()
        log.err('Error while accessing authentication database: %s' % msg)
        if msg.startswith('Checker:'):
            msg=msg.split(':')[1]
        else:
            msg='Error while accessing authentication database.'
        raise failure.Failure(credError.UnauthorizedLogin(msg))


class TwistMind:
    def __init__(self, request, credentials):
        self.request = request
        self.credentials = credentials

class TwistRealm(object):

    implements(portal.IRealm)
    
    def __init__( self, store=None, trace_store=None, poe_store=None, textcha=None):
        self.store = store
        self.trace_store = trace_store
        self.poe_store = poe_store
        self.textcha = textcha

    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:
            if iface is inevow.IResource:
                if avatarId is checkers.ANONYMOUS:
                    return self.createAnonymousAvatar()
                else:
                    return self.createAvatar(avatarId, mind)
            if iface is IXMLRPCAvatar:
                return self.createXMLRPCAvatar(avatarId, mind)
        raise NotImplementedError("Do not support any of the interfaces %s" % (interfaces,))

    def createAnonymousAvatar(self):
        user=TwistUser(username='anonymous',
                       first_name='Anonymous',
                       last_name='User',
                       email='anon@anon.com',
                       role='anon',
                       store=self.store,
                       trace_store=self.trace_store,
                       poe_store=self.poe_store,
                       textcha=self.textcha)
        resc = WelcomePage(user)
        resc.realm = self
        return (inevow.IResource, resc, noLogout)

    
    def createAvatar(self, avatarId, mind):
        
        def _cb(kwr):
            if kwr:
                user=TwistUser(store=self.store, trace_store=self.trace_store, poe_store=self.poe_store, textcha=self.textcha, **kwr[0])
                resc=LoggedInPage(user)
                resc.realm=self
                return (inevow.IResource, resc, self.createLogout(avatarId, mind))
            else:
                log.err('Error while accessing user details')
                return self.createAnonymousAvatar()
                
       
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err('Error while accessing user details: %s' % msg)
            return self.createAnonymousAvatar() 
    
        d = self.store.getSingleUserRecordByUsername(avatarId)
        d.addCallbacks(_cb, _eb)
        
        return d
    
    # CONET
    def createXMLRPCAvatar(self, avatarId, mind):
        
        def _cb(kwr):
            if kwr:
                user=TwistUser(store=self.store, trace_store=self.trace_store, poe_store=self.poe_store, textcha=self.textcha, **kwr[0])
                avatar = XMLRPCAvatar(user)
                return (IXMLRPCAvatar, avatar, lambda: None)
            else:
                log.err('Error while accessing user details')
       
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err('Error while accessing user details: %s' % msg)
    
        d = self.store.getSingleUserRecordByUsername(avatarId)
        d.addCallbacks(_cb, _eb)
        
        return d
    
    def createLogout(self, avatarId, mind):
        def logout():
            session = mind.request.getSession()
            log.msg('Logging avatar %s out of session %s' % (avatarId, session))
            
        return logout
    
class TwistSessionWrapper(SessionWrapper):
      
    def incorrectLoginError(self, error, ctx, segments, loginFailure):
            
        request = inevow.IRequest(ctx)
        e=error.trap(credError.UnauthorizedLogin) ###########
        if e==credError.UnauthorizedLogin:
            msg=error.getErrorMessage()
        else:
            msg=loginFailure

        referer = request.getHeader("referer")
        if referer is not None:
            u = url.URL.fromString(referer)
        else:
            u = urlToChild(ctx, *segments)

        u = u.clear()
        u = u.add('login-failure', msg)
        return u, ()

