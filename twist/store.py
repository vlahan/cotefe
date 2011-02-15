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
import os
import ConfigParser

from twisted.internet import defer
from twisted.enterprise import adbapi
from twisted.python import log, failure, util as tutil

config=ConfigParser.SafeConfigParser()

config.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

dname = config.get('database','name')
dhost = config.get('database', 'host')
duser = config.get('database','user')
dpasswd = config.get('database', 'password')

       
class TwistStore(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('twistedpg',
                                            database=dname,
                                            user=duser,
                                            password=dpasswd,
                                            host=dhost,
                                            cp_reconnect=True)
        self.cache={}
            
    def log_failure(self, f):
        log.err('Store Error: %s' % f.getErrorMessage().strip())
        f.trap(adbapi.ConnectionLost)
        log.err('Store Error: The connection to the database was lost, the operation will not be performed')
        return f

    def dump(self, result):
        log.msg(result)
        
    def checkUsernameExists(self, username):
        sql='''SELECT 1 from users
               WHERE username=%(username)s
            '''
        return self.dbpool.runQuery(sql, {'username':username}).addErrback(self.log_failure)    
    
    def getUserCredentials(self, username):
        sql='''SELECT username, passwd_hash, role, enabled FROM users
               WHERE username=%(username)s
            '''
        return self.dbpool.runQuery(sql, {'username':username}).addErrback(self.log_failure)

 
    def getSingleUserRecordByUsername(self, username):
        sql='''SELECT * FROM users
               WHERE username=%(username)s
            '''
        return self.dbpool.runQuery(sql, {'username':username}).addErrback(self.log_failure)

    def getSingleUserRecord(self, user_id):
        sql='''SELECT * FROM users
               WHERE user_id=%(user_id)s
            '''
        return self.dbpool.runQuery(sql, {'user_id':user_id}).addErrback(self.log_failure)

    def deleteSingleUserRecord(self, user_id):
        sql='''DELETE FROM users
               WHERE user_id=%(user_id)s
            '''
        return self.dbpool.runOperation(sql, {'user_id':user_id}).addErrback(self.log_failure)

    def updateSingleUserRecord(self, **kwr):
        field_names=','.join(['%s=%%(%s)s' % (key, key) for key in kwr.keys()])
        sql='''UPDATE users SET %s''' % field_names
        sql+='''WHERE user_id=%(user_id)s'''
        return self.dbpool.runOperation(sql, kwr).addErrback(self.log_failure)

    def insertSingleUserRecord(self, **kwr):
        field_names=','.join([key for key in kwr.keys()])
        value_names=','.join(['%%(%s)s' % key for key in kwr.keys()])
        sql='''INSERT INTO users (%s)
               VALUES (%s)
            ''' % (field_names, value_names)
        return self.dbpool.runOperation(sql, kwr).addErrback(self.log_failure)

    def getListUserRecords(self, id_list):
        sql='''SELECT * FROM users
               WHERE user_id IN %(id_list)s
               ORDER BY last_name, first_name
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)
        
    def getAllUserRecords(self):
        sql='''SELECT * FROM users
               ORDER BY last_name, first_name
            '''
        return self.dbpool.runQuery(sql).addErrback(self.log_failure)

    def deleteListUserRecords(self, id_list):
        sql='''DELETE FROM users
               WHERE user_id IN %(id_list)s
            '''
        return self.dbpool.runOperation(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)
            
    def refreshAllArchivedJobRecords(self):
        sql='''INSERT INTO arch_jobs (SELECT * FROM jobs AS j
               WHERE (j.time_begin < now()) AND 
               NOT ((now(), j.time_end) OVERLAPS (j.time_begin, j.time_end)));
               DELETE FROM jobs
               WHERE (time_begin < now()) AND
               NOT ((now(), time_end) OVERLAPS (time_begin, time_end));
            '''
        log.msg('Store Message: Refreshing archived job records')
        return self.dbpool.runOperation(sql).addErrback(self.log_failure)

    def getAllArchivedJobRecords(self):
        sql='''SELECT * FROM arch_jobs_users AS j
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql).addErrback(self.log_failure)

    def getAllArchivedMonthJobRecords(self, start_date):
        sql='''SELECT * FROM arch_jobs_users AS j
               WHERE (time_begin, time_end) OVERLAPS (%(start_date)s, INTERVAL '1 month')
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql,{'start_date':start_date}).addErrback(self.log_failure)
    
    def getListArchivedJobRecords(self, id_list):
        sql='''SELECT * FROM arch_jobs_users AS j
               WHERE j.job_id IN %(id_list)s
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)
    
    def deleteListArchivedJobRecords(self, id_list):
        sql='''DELETE FROM arch_jobs
               WHERE job_id IN %(id_list)s
            '''
        return self.dbpool.runOperation(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)
   
    def getAllJobRecords(self):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE j.time_begin > now() OR (now(), time_end) OVERLAPS (time_begin, time_end)
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql).addErrback(self.log_failure)

    def getAllMonthJobRecords(self, start_date):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE ((time_begin, time_end) OVERLAPS (%(start_date)s, INTERVAL '1 month')) AND
                      (time_begin > now() OR (now(), time_end) OVERLAPS (time_begin, time_end))    
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql,{'start_date':start_date}).addErrback(self.log_failure)


    def getAllOwnJobRecords(self, user_id):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE j.time_begin > now() OR (now(), time_end) OVERLAPS (time_begin, time_end)
               AND j.user_id=%(user_id)s
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql, {'user_id':user_id}).addErrback(self.log_failure)

    def getSingleJobRecord(self, job_id):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE j.job_id=%(job_id)s
               AND (j.time_begin > now() OR (now(), time_end) OVERLAPS (time_begin, time_end))
            '''
        return self.dbpool.runQuery(sql, {'job_id':job_id}).addErrback(self.log_failure)

    def getSingleOwnJobRecord(self, job_id, user_id):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE j.job_id=%(job_id)s
               AND j.user_id=%(user_id)s
               AND (j.time_begin > now() OR (now(), time_end) OVERLAPS (time_begin, time_end))
            '''
        return self.dbpool.runQuery(sql, {'job_id':job_id, 'user_id':user_id}).addErrback(self.log_failure)

    def getListJobRecords(self, id_list):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE j.job_id IN %(id_list)s
               AND (j.time_begin > now() OR (now(), time_end) OVERLAPS (time_begin, time_end))
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)

    def getListOwnJobRecords(self, id_list, user_id):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE j.job_id IN %(id_list)s
               AND j.user_id=%(user_id)s
               AND (j.time_begin > now() OR (now(), time_end) OVERLAPS (time_begin, time_end))
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list), 'user_id':user_id}).addErrback(self.log_failure)

    def getListArchivedAndCurrentJobRecords(self, id_list):
        sql='''SELECT * FROM arch_current_jobs_users AS j
               WHERE j.job_id IN %(id_list)s
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)

    def getListOwnArchivedAndCurrentJobRecords(self, id_list, user_id):
        sql='''SELECT * FROM arch_current_jobs_users AS j
               WHERE j.job_id IN %(id_list)s
               AND j.user_id=%(user_id)s
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list), 'user_id':user_id}).addErrback(self.log_failure)



    def getAllActiveJobRecords(self):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE active
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql).addErrback(self.log_failure)

    def getAllOwnActiveJobRecords(self, user_id):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE active
               AND j.user_id=%(user_id)s
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql, {'user_id':user_id}).addErrback(self.log_failure)

    def getSingleActiveJobRecord(self, job_id):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE active
               AND j.job_id=%(job_id)s
            '''
        return self.dbpool.runQuery(sql, {'job_id':job_id}).addErrback(self.log_failure)

    def getSingleOwnActiveJobRecord(self, job_id, user_id):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE active
               AND j.job_id=%(job_id)s
               AND j.user_id=%(user_id)s
            '''
        return self.dbpool.runQuery(sql, {'job_id':job_id, 'user_id':user_id}).addErrback(self.log_failure)

    def getListActiveJobRecords(self, id_list):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE active
               AND j.job_id IN %(id_list)s
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)

    def getListOwnActiveJobRecords(self, id_list, user_id):
        sql='''SELECT * FROM jobs_users_is_active AS j
               WHERE active
               AND j.job_id IN %(id_list)s
               AND j.user_id=%(user_id)s
               ORDER BY time_begin
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list), 'user_id':user_id}).addErrback(self.log_failure)

    def deleteListJobRecords(self, id_list):
        sql='''DELETE FROM jobs
               WHERE job_id IN %(id_list)s
            '''
        return self.dbpool.runOperation(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)

    def deleteListOwnJobRecords(self, id_list, user_id):
        sql='''DELETE FROM jobs
               WHERE job_id IN %(id_list)s AND user_id=%(user_id)s
            '''
        return self.dbpool.runOperation(sql, {'id_list':tuple(id_list), 'user_id':user_id}).addErrback(self.log_failure)

    def insertSingleJobRecord(self, **kwr):
        field_names=','.join([key for key in kwr.keys()])
        value_names=','.join(['%%(%s)s' % key for key in kwr.keys()])
        sql='''INSERT INTO jobs (%s)
               VALUES (%s)
            ''' % (field_names, value_names)
        return self.dbpool.runOperation(sql, kwr).addErrback(self.log_failure)

    def updateSingleJobRecord(self, **kwr):
        field_names=','.join(['%s=%%(%s)s' % (key, key) for key in kwr.keys()])
        sql= '''UPDATE jobs SET %s''' % field_names
        sql+='''WHERE job_id=%(job_id)s
             '''
        return self.dbpool.runOperation(sql, kwr).addErrback(self.log_failure)
 
    def updateSingleOwnJobRecord(self, **kwr):
        field_names=','.join(['%s=%%(%s)s' % (key, key) for key in kwr.keys()])
        sql= '''UPDATE jobs SET %s''' % field_names
        sql+='''WHERE job_id=%(job_id)s
                AND user_id=%(user_id)s
             '''
        return self.dbpool.runOperation(sql, kwr).addErrback(self.log_failure)
    
    def getPlatformOptions(self):
        sql='''SELECT platform_id, name_short FROM platforms
               ORDER BY name_short'''
        return self.dbpool.runQuery(sql).addErrback(self.log_failure)
   
    def getAllBindedNodeRecords(self):
        sql='''SELECT n.node_id FROM node_deployments as n
               ORDER BY n.node_id
            '''
        return self.dbpool.runQuery(sql).addErrback(self.log_failure)

    def getAllBindedPlatformNodeRecords(self, platform_id):
        sql='''SELECT n.node_id FROM node_deployments as n
               WHERE n.platform_id=%(platform_id)s
               ORDER BY n.node_id
            '''
        return self.dbpool.runQuery(sql, {'platform_id':platform_id}).addErrback(self.log_failure)
    
    def getListBindedNodeRecords(self, id_list):
        sql='''SELECT n.node_id FROM node_deployments as n
               WHERE n.node_id IN %(id_list)s
               ORDER BY n.node_id
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)
        
    def getListBindedPlatformNodeRecords(self, id_list, platform_id):
        sql='''SELECT n.node_id FROM node_deployments as n
               WHERE n.platform_id=%(platform_id)s 
               AND n.node_id IN %(id_list)s
               ORDER BY n.node_id
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list), 'platform_id':platform_id}).addErrback(self.log_failure)
        
    def getNodeListPlatformArrrayRecord(self, id_list):
        sql='''SELECT array_accum(DISTINCT platform_id) as resources FROM node_deployments as n
               WHERE n.node_id IN %(id_list)s
            '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)
            
    def getAllNodeSupernodeBindingRecords(self):
        sql = '''SELECT * FROM node_supernode_bindings'''
        return self.dbpool.runQuery(sql).addErrback(self.log_failure)        

    def getListNodeSupernodeBindingRecords(self, id_list):
        sql='''SELECT * FROM node_supernode_bindings
               WHERE node_id IN %(id_list)s'''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)

    def getPlatform(self, id_list):
        sql='''SELECT DISTINCT(platform_id) from nodes where node_id IN %(id_list)s
        '''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)

    
    def getAllDeployedSupernodeAddressRecords(self, cached=True):
        records=self.cache.get('getAllDeployedSupernodeAddressRecord', None)
        if cached and records is not None:
            return defer.succeed(records)
        else:
            sql = '''SELECT DISTINCT * FROM supernode_deployment_addresses
                  ORDER BY supernode_id
                  '''
            d=self.dbpool.runQuery(sql).addErrback(self.log_failure)
            d.addCallback(self._cb_cache, 'getAllDeployedSupernodeAddressRecord')
            return d


    def getListDeployedSupernodeAddressRecords(self, id_list):
        sql='''SELECT DISTINCT * FROM supernode_deployment_addresses
               WHERE supernode_id IN %(id_list)s'''
        return self.dbpool.runQuery(sql, {'id_list':tuple(id_list)}).addErrback(self.log_failure)

    def _cb_cache(self, records, key):
        self.cache[key]=records
        return defer.succeed(records)
