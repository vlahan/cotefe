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


import sha
import base64
import os
import ConfigParser
from twisted.internet import defer, threads
from twisted.python import log, util as tutil

from burn import burn

config=ConfigParser.SafeConfigParser()

config.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

node_blacklist_string = config.get('maintenance','node_blacklist')
node_blacklist=[int(id) for id in node_blacklist_string.split(',')]


def passwd_encode(passwd):
    return base64.b64encode("twistSlT$"+ sha.new("twistSlT$%s" % passwd).digest())

class TwistUser(object):
    
    def __init__(self, store=None, trace_store=None, poe_store=None, textcha=None, **kwr):
        self.store=store
        self.trace_store=trace_store
        self.poe_store=poe_store
        self.textcha=textcha
        self.user_id=kwr.get('user_id', None)
        self.username=kwr['username']
        self.first_name=kwr['first_name']
        self.last_name=kwr['last_name']
        self.email=kwr['email']
        self.role=kwr['role']
    
    def checkUsernameExists(self, username):
        return self.store.checkUsernameExists(username)
          
    def requestAccount(self, data):
        user=dict((i, data[i]) for i in ['username', 'first_name', 'last_name', 'email'])
        user['passwd_hash']=passwd_encode(data['passwd'])
        user['role']='requested'
        user['enabled']=False
        d=self.store.insertSingleUserRecord(**user)
        return d

    
    def getAllUsers(self):
        if self.role=='admin':
            return self.store.getAllUserRecords()
        else:
            return []

    def getListUsers(self, id_list):
        if self.role=='admin':
            return self.store.getListUserRecords(id_list)
        else:
            return []

    def getSingleUser(self, user_id):
        if self.role=='admin':
            return self.store.getSingleUserRecord(user_id)
        elif self.role=='user':
            return self.store.getSingleUserRecord(self.user_id)

    def deleteSingleUser(self, user_id):
        if self.role=='admin':
            return self.store.deleteSingleUserRecord(user_id)
        elif self.role=='user':
            return self.store.deleteSingleUserRecord(self.user_id)


    def deleteListUsers(self, id_list):
        return self.store.deleteListUserRecords(id_list)
    
    def updateSingleUser(self, user_id, data):
        user=dict((i, data[i]) for i in ['first_name', 'last_name', 'enabled', 'role'])
        if self.role=='admin':
            user['user_id']=user_id
        elif self.role=='user':
            user['user_id']=self.user_id
        if data['passwd']:
            user['passwd_hash']=passwd_encode(data['passwd'])
            del data['passwd']
        return self.store.updateSingleUserRecord(**user)
    
    def addSingleUser(self, data):
        user=dict((i, data[i]) for i in ['username', 'first_name', 'last_name', 'email', 'enabled', 'role'])
        user['passwd_hash']=passwd_encode(data['passwd'])
        return self.store.insertSingleUserRecord(**user)
    
    def userRoleOptions(self):
        return [('admin', 'admin'), 
                ('user', 'user'),
                ('requested','requested'),
                ]
    
    def refreshAllArchivedJobs(self):
        if self.role=='admin': 
            return self.store.refreshAllArchivedJobRecords()
        else:
            return []

    def getAllArchivedJobs(self):
        if self.role in ('admin', 'user'): 
            return self.store.getAllArchivedJobRecords()
        else:
            return []

    def getAllArchivedMonthJobs(self, start_date):
        if self.role in ('admin', 'user'): 
            return self.store.getAllArchivedMonthJobRecords(start_date)
        else:
            return []

    def getListArchivedJobs(self, id_list):
        if self.role=='admin':
            return self.store.getListArchivedJobRecords(id_list)
        else:
            return []

    def purgeListArchivedJobs(self, id_list):
        if self.role=='admin':
            return self.store.deleteListArchivedJobRecords(id_list)
        else:
            return defer.failure()
        
    def getAllJobs(self):
        if self.role=='admin': 
            return self.store.getAllJobRecords()
        elif self.role=='user':
            return self.store.getAllJobRecords()
        else:
            return []

    def getAllMonthJobs(self, start_date):
        if self.role=='admin': 
            return self.store.getAllMonthJobRecords(start_date)
        elif self.role=='user':
            return self.store.getAllMonthJobRecords(start_date)
        else:
            return []

    def getListAllJobs(self, id_list):
        if self.role in ['admin', 'user']:
            return self.store.getListJobRecords(id_list)
        else:
            return []

    
    def getListJobs(self, id_list):
        if self.role=='admin':
            return self.store.getListJobRecords(id_list)
        elif self.role=='user':
            return self.store.getListOwnJobRecords(id_list, self.user_id)
        else:
            return []

    def getListArchivedAndCurrentJobs(self, id_list):
        if self.role=='admin':
            return self.store.getListArchivedAndCurrentJobRecords(id_list)
        elif self.role=='user':
            return self.store.getListOwnArchivedAndCurrentJobRecords(id_list, self.user_id)
        else:
            return []


    def getSingleJobAllTraces(self, job_id):
        def _cb(r):
            if r:
                return self.trace_store.getJobAllTraceFiles(job_id)
            else:
                return []
        d=self.getListArchivedAndCurrentJobs([job_id]).addCallback(_cb)
        return d

    def getSingleJobListTraces(self, job_id, name_list):
        def _cb(r):
            if r:
                return self.trace_store.getJobListTraceFiles(job_id, name_list)
            else:
                return []
        d=self.getListArchivedAndCurrentJobs([job_id]).addCallback(_cb)
        return d

    def deleteSingleJobListTraces(self, job_id, name_list):
        def _cb(r):
            if r:
                return self.trace_store.deleteJobListTraceFiles(job_id, name_list)
            else:
                return []
        d=self.getListArchivedAndCurrentJobs([job_id]).addCallback(_cb)
        return d

    def deleteSingleJobTracesDir(self, job_id):
        def _cb(r):
            if r:
                return self.trace_store.deleteJobTraceDir(job_id)
        d=self.getListArchivedAndCurrentJobs([job_id]).addCallback(_cb)
        return d

    def getTraceServerMaxPacketSize(self):
        return self.trace_store.getRemoteMaxPacketSize()
    
    def openTraceForReading(self, job_id, trace_name):
        def _cb(r):
            if r:
                return self.trace_store.openJobTraceFile(job_id, trace_name)
        return self.getListArchivedAndCurrentJobs([job_id]).addCallback(_cb)
         

    def getSingleJob(self, job_id):
        if self.role=='admin':
            return self.store.getSingleJobRecord(job_id)
        elif self.role=='user':
            return self.store.getSingleOwnJobRecord(job_id, self.user_id)
        else:
            return []


    def getAllActiveJobs(self):
        if self.role in ('admin', 'user'): 
            return self.store.getAllActiveJobRecords()
        else:
            return []

    def getListAllActiveJobs(self, id_list):
        if self.role in ('admin', 'user'):
            return self.store.getListActiveJobRecords(id_list)
        else:
            return []
    
    def getListActiveJobs(self, id_list):
        if self.role=='admin':
            return self.store.getListActiveJobRecords(id_list)
        elif self.role=='user':
            return self.store.getListOwnActiveJobRecords(id_list, self.user_id)
        else:
            return []


    def getSingleActiveJob(self, job_id):
        if self.role=='admin':
            return self.store.getSingleActiveJobRecord(job_id)
        elif self.role=='user':
            return self.store.getSingleOwnActiveJobRecord(job_id, self.user_id)
        else:
            return []

    def deleteListJobs(self, id_list):
#        for job_id in id_list:
#            self.trace_store.controlJobTracing('delete_job', job['job_id'], '', {})
        if self.role=='admin':
            return self.store.deleteListJobRecords(id_list)
        elif self.role=='user':
            return self.store.deleteListOwnJobRecords(id_list, self.user_id)
        
    def updateSingleJob(self, job_id, data):
        job=dict((i, data[i]) for i in ['description', 'time_begin', 'time_end', 'resources'])
        job['job_id']=job_id
#        self.trace_store.controlJobTracing('update_job', job['job_id'], job['time_end'], {})
        if self.role=='admin':
            return self.store.updateSingleJobRecord(**job)
        elif self.role=='user':
            job['user_id']=self.user_id
            return self.store.updateSingleOwnJobRecord(**job)
                
    def addSingleJob(self, data):
        job=dict((i, data[i]) for i in ['description', 'time_begin', 'time_end', 'resources'])
        job['user_id']=self.user_id
        return self.store.insertSingleJobRecord(**job)

    def getPlatformOptions(self, res):
        def _cb(platforms):
            k={}
            for p in platforms:
                k[p['platform_id']]=p['name_short']
            l=[]
            for r in res:
#                r['resources']=[k[q] for q in r['resources']]
                l.append(r)
            return l
        return self.store.getPlatformOptions().addCallback(_cb)
        
    def getAllBindedNodes(self):
        if self.role in ('admin', 'user'):
            return self.store.getAllBindedNodeRecords()
        else:
            return []

    def getAllBindedPlatformNodes(self, platform_id):
        if self.role in ('admin', 'user'):
            def _cb(r):
                return [node for node in r if node['node_id'] not in node_blacklist]
            
            d=self.store.getAllBindedPlatformNodeRecords(platform_id).addCallback(_cb)
            return d
        else:
            return []
        
    def getListBindedNodeRecords(self, id_list):
        if self.role in ('admin', 'user'):
            def _cb(r):
                return [node for node in r if node['node_id'] not in node_blacklist]
            
            d=self.store.getListBindedNodeRecords(id_list).addCallback(_cb)
            return d
        else:
            return []
              
    def getNodeListPlatformArrray(self, id_list):
        if self.role in ('admin', 'user'):
            return self.store.getNodeListPlatformArrrayRecord(id_list)
        else:
            return []
    
    def getListNodeSupernodeBindings(self, id_list):
        if self.role in ('admin', 'user'):
            return self.store.getListNodeSupernodeBindingRecords(id_list)
        else:
            return []
    
    def executeOldBurnAction(self, action):
        if self.role in ('admin', 'user'):
            return threads.deferToThread(burn, action)
        else:
            return ''

    def controlJobTracing(self, action, job_id, time_end, act_node_set):
        if self.role in ('admin', 'user'):
            def _cb(bindings):
                if bindings:
                    ans_dict={}
                    for binding in bindings:
                        ans_dict.setdefault(binding['node_id'], binding['supernode_id'])
                        
                    return self.trace_store.controlJobTracing(action, job_id, time_end, ans_dict)
                else:
                    msg = 'Empty node supernode binding set'
                    return 'Trace Control Action %s failed: %s' % (action, msg)
            
            def _eb(f):
                msg=f.getErrorMessage().strip()
                return 'Trace Control Action %s failed: %s' % (action, msg)
            
            return self.store.getListNodeSupernodeBindingRecords(act_node_set).addCallbacks(_cb, _eb)
        else:
            return ''
    
    def getAllSupernodes(self, cached=True):
        if self.role in ('user', 'admin'):
            d1=self.store.getAllDeployedSupernodeAddressRecords(cached)
            d2=self.poe_store.get_supernode_status(cached)
            dl=defer.DeferredList([d1,d2])
            dl.addCallback(self._cb_getAllSupernodes)
            return dl
        else:
            return []

    def _cb_getAllDeployedSupernodeAddressRecords(self, records):
        self.installed_supernodes=records

    def _cb_getAllSupernodes(self, data):
        success_deployment, data_deployment = data[0]
        success_status, data_status = data[1]
        if success_deployment and success_status:
            for supernode in data_deployment:
                status=data_status.get(supernode['mac_addr'], 'unknown')
                supernode['status']=status
            return data_deployment
        else:
            return []
    
    def getListSupernodes(self, id_list, cached=True):
        if self.role in ('user','admin'):
            d=self.getAllSupernodes(cached)
            d.addCallback(self._cb_getListSupernodes, id_list)
            return d
        else:
            return []

    def _cb_getListSupernodes(self, supernodes, id_list):
        return [supernode for supernode in supernodes if supernode['supernode_id'] in id_list]

    def controlListSupernodes(self, id_list, action, cached=True):
        if self.role in ('admin'):
            d=self.getListSupernodes(id_list, cached)
            d.addCallback(self._cb_controlListSupernodes, action)
            return d
        else:
            return ''

    def _cb_controlListSupernodes(self, supernodes, action):
        mac_list=[supernode['mac_addr'] for supernode in supernodes]
        return self.poe_store.control_supernode_power(mac_list, action)
    
    def getAllPlatforms(self):
        if self.role=='admin': 
            return self.store.getAllPlatformRecords()
        elif self.role=='user':
            return self.store.getAllPlatformRecords()
        else:
            return []
        
        
