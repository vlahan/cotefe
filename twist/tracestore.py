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
import re
import datetime
import base64
import struct

import ConfigParser

from twisted.conch.client import direct, default, options
from twisted.conch.ssh import connection, keys, common, channel, filetransfer, userauth
from twisted.conch import error
from twisted.internet import reactor, defer, protocol
from twisted.python import log, util as tutil
    
config=ConfigParser.SafeConfigParser()

config.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

thost = config.get('traces','server_host')
tport = config.getint('traces', 'server_port')
tpath = config.get('traces','server_store_path')

tuser = config.get('traces','client_user')
tpasswd = config.get('traces', 'client_password')
tsshdir = config.get('traces', 'client_ssh_dir')
tpphrase = config.get('traces', 'client_passphrase')

try:
    tpubkey = config.get('traces', 'client_pubkey')
    tprivkey = config.get('traces', 'client_privkey')
except ConfigParser.NoOptionError:
    tpubkey=None
    tprivkey=None

trace_re = re.compile(r'^nde(?P<node_id>\d+)\.')

class TwistTraceConnection(connection.SSHConnection):
    
    def __init__(self):
        connection.SSHConnection.__init__(self)
        self.tracesesson=None
        
    def serviceStarted(self):
        self.tracesesson=TwistTraceSession()
        self.openChannel(self.tracesesson)
        
    def adjustWindow(self, channel, bytesToAdd):
        # Monkey patch to disable the nasty log.msg in parent
        if channel.localClosed:
            return # we're already closed
        self.transport.sendPacket(connection.MSG_CHANNEL_WINDOW_ADJUST, struct.pack('>2L',
                                    self.channelsToRemoteChannel[channel],
                                    bytesToAdd))
        channel.localWindowLeft += bytesToAdd

class TwistTraceSession(channel.SSHChannel):

    name = 'session'
        
    def channelOpen(self, foo):
        d = self.conn.sendRequest(self, 'subsystem', common.NS('sftp'), wantReply=1)
        d.addCallbacks(self._cbSubsystem, self._ebSubsystem)
        return d
    
    def channelFailed(self, reason):
        log.msg('Trace Store: Error opening SSH channel to server: %s' % reason)

    def _cbSubsystem(self, result):
        self.client = filetransfer.FileTransferClient()
        self.client.makeConnection(self)
        self.dataReceived = self.client.dataReceived
        self.conn.traceclient=self.client

    def _ebSubsystem(self, f):
        log.msg('Trace Store: Error requesting sftp subsystem from server')
        log.err(f)

    def extReceived(self, t, data):
        pass
    
    def eofReceived(self):
        log.msg('Trace Store: Got EOF from the other side!')
    
    def closeReceived(self):
        log.msg('Trace Store: Remote side closed %s' % self)

    def closed(self):
        log.msg('Trace Store: Both sides closed %s' % self)

class TwistTraceUserAuthClient(userauth.SSHUserAuthClient):
    
    def getPassword(self):
        return defer.succeed(tpasswd)
            
    def getPublicKey(self):
        try:
            return keys.Key.fromFile(filename=tpubkey).blob()
        except IOError, e:
            log.err('Bad public key file', e)
            return defer.fail()
        except keys.BadKeyError, e:
            log.err('Bad public key', e)
            return defer.fail()
    
    def getPrivateKey(self):
        try:
            return defer.succeed(keys.Key.fromFile(filename=tprivkey, passphrase=tpphrase).keyObject)
        except IOError, e:
            log.err('Bad private key file', e)
            return defer.fail()
        except (keys.BadKeyError, keys.EncryptedKeyError):
            log.err('Bad private key')
            return defer.fail()

class TwistSSHClientTransport(direct.SSHClientTransport):
    
    def connectionMade(self):
        self.factory.resetDelay()
        direct.SSHClientTransport.connectionMade(self)

class TwistSSHClientFactory(protocol.ReconnectingClientFactory):
    maxDelay = 60
    
    def __init__(self, d, options, verifyHostKey, userAuthObject):
        self.d = d
        self.options = options
        self.verifyHostKey = verifyHostKey
        self.userAuthObject = userAuthObject
        

    def clientConnectionLost(self, connector, reason):
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


    def buildProtocol(self, addr):
        trans = TwistSSHClientTransport(self)
        if self.options['ciphers']:
            trans.supportedCiphers = self.options['ciphers']
        if self.options['macs']:
            trans.supportedMACs = self.options['macs']
        if self.options['compress']:
            trans.supportedCompressions[0:1] = ['zlib']
        if self.options['host-key-algorithms']:
            trans.supportedPublicKeys = self.options['host-key-algorithms']
        return trans


def verifyHostKey(transport, host, pubKey, fingerprint):
    goodKey = isInKnownHosts(host, pubKey, transport.factory.options)
    if goodKey == 1:
        return defer.succeed(1)
    elif goodKey == 2:
        return defer.fail(error.ConchError('Changed host key'))
    else:
        return defer.fail(error.ConchError('Error during host key verification'))
        
def isInKnownHosts(host, pubKey, options):
    keyType = common.getNS(pubKey)[0]
    retVal = 0
    
    kh_file = options['known-hosts'] or '%s/known_hosts' % tsshdir
    try:
        known_hosts = open(os.path.expanduser(kh_file))
    except IOError:
        return 0
    for line in known_hosts:
        split = line.split()
        if len(split) < 3:
            continue
        hosts, hostKeyType, encodedKey = split[:3]
        if host not in hosts.split(','):
            continue
        if hostKeyType != keyType:
            continue
        try:
            decodedKey = base64.decodestring(encodedKey)
        except:
            continue
        if decodedKey == pubKey:
            return 1
        else:
            retVal = 2
    return retVal


class TwistTraceStore(object):
    
    def __init__(self):
        self.opt = options.ConchOptions()
        self.vhk = verifyHostKey
        self.conn = TwistTraceConnection()
        self.uao = TwistTraceUserAuthClient(tuser, self.conn)
        self.d=defer.Deferred()
        self.connect()
        
    def connect(self, f=None):
        d, self.d = self.d, None
        factory = TwistSSHClientFactory(self.d, self.opt, self.vhk, self.uao)
        reactor.connectTCP(thost, tport, factory)
        d.addErrback(self._eb_connect)

    def log_msg(self, r):
        log.msg('Trace Store: %s' % r)
    
    def _eb_connect(self, f):
        log.err('Trace Store Error: %s' % f.getErrorMessage().strip())
        
    def _eb_list(self, f, job_id):
        f.trap(filetransfer.SFTPError, EOFError)
        log.err('Trace Store Error: %s while listing traces for job %s' % (f.getErrorMessage().strip(), job_id))
        return []

    def _eb_delete(self, f):
        log.err('Trace Store Error: %s' % f.getErrorMessage().strip())
        raise f
    
    def _eb_open(self, f):
        log.err('Trace Store Error: %s' % f.getErrorMessage().strip())
        raise f
    
    def _dirOpened(self, directory):
        return directory.read()
    
    def _dirAllRead(self, file_list):
        trace_list=[]
        for f in file_list:
            name, txtinfo, attrs = f
            trace_list.append({'name':name, 'size':attrs['size'], 'time':attrs['atime']})
        trace_list.sort(key=lambda l: l['time'])
        trace_list.reverse()
        return trace_list

    def _dirListRead(self, file_list, name_list):
        trace_list=[]
        for f in file_list:
            name, txtinfo, attrs = f
            if name in name_list:
                trace_list.append({'name':name, 'size':attrs['size'], 'time':attrs['atime']})
        trace_list.sort(key=lambda l: l['time'])
        trace_list.reverse()
        return trace_list

    def _dirRemoveIfEmpty(self, file_list, job_id):
        if not file_list:
            return self.conn.traceclient.removeDirectory('%s' % job_id)

    def getJobAllTraceFiles(self, job_id):       
        d=self.conn.traceclient.openDirectory('%s' % job_id)
        d.addCallback(self._dirOpened)
        d.addCallback(self._dirAllRead)
        d.addErrback(self._eb_list, job_id)
        return d

    def getJobListTraceFiles(self, job_id, name_list):       
        d=self.conn.traceclient.openDirectory('%s' % job_id)
        d.addCallback(self._dirOpened)
        d.addCallback(self._dirListRead, name_list)
        d.addErrback(self._eb_list, job_id)
        return d

    def deleteJobListTraceFiles(self, job_id, name_list):
        l=[]
        for name in name_list:
            d=self.conn.traceclient.removeFile('%s/%s' % (job_id, name))
            d.addErrback(self._eb_delete)
            l.append(d)
        dl=defer.DeferredList(l)
        dl.addErrback(self._eb_delete)
        return dl
    
    def deleteJobTraceDir(self, job_id):
        d=self.getJobAllTraceFiles(job_id)
        d.addCallback(self._dirRemoveIfEmpty, job_id)
        d.addErrback(self._eb_delete)
        return d

    def openJobTraceFile(self, job_id, trace_name):
        d = self.conn.traceclient.openFile('%s/%s' % (job_id, trace_name), filetransfer.FXF_READ, {})
        d.addCallback(self._fileOpened)
        d.addErrback(self._eb_open)
        return d
        
    def _fileOpened(self, trace_file):
        d=trace_file.getAttrs()
        d.addCallback(self._gotAttrs, trace_file)
        d.addErrback(self._eb_open)
        return d
    
    def _gotAttrs(self, attrs, trace_file):
        return trace_file, attrs['size']
    
    def getRemoteMaxPacketSize(self):
        if self.conn:
            return self.conn.tracesesson.remoteMaxPacket
        else:
            return 0
    
    def marshalControlData(self, job_id, time_end, ans_dict):
        ans_data=','.join('%s_%s' % (id_key,  ans_dict[id_key]) for id_key in ans_dict)
        return '%s;%s;%s' % (job_id, time_end.strftime('%Y-%m-%d %H:%M:%S'), ans_data)
    
    def controlJobTracing(self, action, job_id, time_end, ans_dict):
        
        def _cb(r, action):
            return 'Trace Control Action %s was successful: %s' % (action, r)

        def _eb(f, action):
            msg=f.getErrorMessage().strip()
            log.err('Trace Store Error: %s' % msg)
            return 'Trace Control Action %s failed: %s' % (action, msg)
        
        d=self.conn.traceclient.extendedRequest(action, self.marshalControlData(job_id, time_end, ans_dict))
        d.addCallback(_cb, action)
        d.addErrback(_eb, action)
        return d

        
