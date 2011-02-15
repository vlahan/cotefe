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
# import magic
import shutil

from twisted.internet import defer
from twisted.python import log, failure, lockfile, util as tutil
from zope.interface import implements
from nevow import inevow, tags as T, url, util as nutil

import formal

import base

import ConfigParser

config=ConfigParser.SafeConfigParser()

config.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

lpath = config.get('web','temp_path')

nullapppath = config.get('web','tools_path') + '/'

rlockfile=config.get('web', 'lock_file')

try:
    lockfile.FilesystemLock(rlockfile).unlock()
except (OSError, ValueError):
    pass

nlist_name = config.get('web','node_list')
slist_name = config.get('web','slug_list')
ilist_name = config.get('web','image_list')


class TwistFileUploadWidget(formal.FileUploadWidget):
#monkey patch to support non-existing keys

    def processInput(self, ctx, key, args):
        resourceManager = formal.iformal.IForm( ctx ).resourceManager
        self._registerWithResourceManager( key, args, resourceManager )
        try:
            fileitem = inevow.IRequest(ctx).fields[key]
        except KeyError:
            return self.original.validate((None, None, None))
        name = fileitem.filename.decode(nutil.getPOSTCharset(ctx))
        if name:
            resourceManager.setResource( key, fileitem.file, name )
        value = resourceManager.getResourceForWidget( key )
        value = self.convertibleFactory(self.original).toType( value )
        if self.removeable is True:
            remove = args.get('%s_remove'%key, [None])[0]
            if remove is not None:
                value = (None,None,None)
        return self.original.validate( value )


    
class TwistImageFileValidator(object):
    implements(formal.iformal.IValidator)
    
    def validate(self, field, value):
        if value and value[1] is not None:
            (t, f, n)=value
            ms = magic.open(magic.MAGIC_NONE)
            ms.load()
            type=ms.buffer(f.read(32))
            f.seek(0)
            if not type.startswith('ELF 32-bit LSB executable'):
                raise formal.FieldValidationError(u'The uploaded file is not an ELF executable')  
            


class ControlJobPage(base.AuthenticatedTwistPage):
    
    def __init__(self, user):
        super(ControlJobPage, self).__init__(user)
        self.id_list=[]
        self.ajobs=[]
        self.job={}
        self.res_node_set=set()
        self.act_node_set=set()
        self.lockobj=lockfile.FilesystemLock(rlockfile)
           
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Job Management'],
                           T.h3['Controlling active job:'],                           
                           T.invisible(data=T.directive('ajobs'), render=T.directive('if'))[
                               T.div(pattern='True')[
                                    T.table(render=T.directive('sequence'))[
                                        T.tr(pattern='header', render=T.directive('header')),
                                        T.tr(pattern='item', class_='rowA', render=T.directive('ajob_item')),
                                        T.tr(pattern='item', class_='rowB', render=T.directive('ajob_item')),
                                    ],
                                   T.div(render=T.directive('form controlJob')),
                               ],
                               T.div(pattern='False')[
                                   T.p['''You have insufficient rights for the operation or 
                                          you are trying to control a non-existing active job.''',
                                       T.span(render=T.directive('back_link'))
                                   ]
                               ]
                           ]
                       ]
#                   ]
               ]
    
    def data_ajobs(self, ctx, data):
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['job_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                return []
        return self.user.getListActiveJobs(self.id_list)
    
    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='10%')['Id'],
                       T.th(width='20%')['Description'],
                       T.th(width='20%')['Owner'], 
                       T.th(width='20%')['Resources'],
                       T.th(width='15%')['Start'], 
                       T.th(width='15%')['End'],
                       ]
    
    
    def render_ajob_item(self, ctx, job):
        style='active'
        return ctx.tag[
                  T.td(_class=style)[job['job_id']],
                  T.td(_class=style)[job['description']],
                  T.td(_class=style)['%s %s' % (job['first_name'], job['last_name']),
                       T.br(), 
                       job['email']
                  ],
                  T.td(_class=style, render=T.directive('platforms')),
                  T.td(_class=style)[job['time_begin']],
                  T.td(_class=style)[job['time_end']]
                ]
    
    def render_platforms(self, ctx, job):
        if job['resources'] is not None:
            res=[T.li[base.pl_map[r]] for r in job['resources']]
            return ctx.tag[T.ul[res]]
        else:
            return ctx.tag
    
    def form_controlJob(self, ctx):
        
        sf_speed_options=[(0,'None'),
                          (115200, '115200'), 
                          (57600, '57600'),
                          (38400, '38400'),
                          (19200, '19200'),
                          (9600, '9600'),
                          (4800, '4800')]
        
        sf_version_options=[(1,'TinyOS 1.x'),
                            (2,'TinyOS 2.x')]
                         
        channel_options=[(i,str(i)) for i in range(11,27)] 
                               
        def addControlField(f, g, index):
            sub_g=formal.Group('grp%s' % index, label='Control group %s' % index)
            
            sub_g.add(formal.Field('nodes',
                               formal.String(validators=[formal.PatternValidator(r'^\s*((\d+\s+)*|(\d+))+$')]),
                               formal.widgetFactory(formal.TextArea),
                               label='Node list'))
            
            sub_g.add(formal.Field('image',
                               formal.File(validators=[TwistImageFileValidator()]),
                               formal.widgetFactory(TwistFileUploadWidget),
                               label='Image'))
            
            sub_g.add(formal.Field('sfspeed',
                               formal.Integer(),
                               formal.widgetFactory(formal.SelectChoice, options=sf_speed_options),
                               label='SF Baudrate'))
            f.data.setdefault('ctrl.grp%s.sfspeed' % index, 0)
                                   
            sub_g.add(formal.Field('sfversion',
                               formal.Integer(),
                               formal.widgetFactory(formal.SelectChoice, options=sf_version_options),
                               label='SF Version'))
            f.data.setdefault('ctrl.grp%s.sfversion' % index, 2)
            
            sub_g.add(formal.Field('channel',
                               formal.Integer(),
                               formal.widgetFactory(formal.SelectChoice, options=channel_options),
                               label='Channel'))
            f.data.setdefault('ctrl.grp%s.channel' % index, 26)
            g.add(sub_g)
        
        def addActionFields(f):
            f.addAction(self.installAction, name='install', label='Install')
            f.addAction(self.eraseAction, name='erase', label='Erase')
            f.addAction(self.resetAction, name='reset', label='Reset')
            f.addAction(self.powerOnAction, name='power_on', label='Power On')
            f.addAction(self.powerOffAction, name='power_off', label='Power Off')
            f.addAction(self.startSFAction, name='start_sf', label='Start SF')
            f.addAction(self.stopSFAction, name='stop_sf', label='Stop SF')
            f.addAction(self.startTracingAction, name='start_tracing', label='Start Tracing')
            f.addAction(self.stopTracingAction, name='stop_tracing', label='Stop Tracing')
            return f
                
        def addResourceField(f, g, platform_id):
            def _cb(res):
                if res:
                    key='p%s' % platform_id
                    label='%s nodes' % base.pl_map[platform_id]           
                    g.add(formal.Field(key,
                                       formal.String(immutable=True),
                                       formal.widgetFactory(formal.TextArea),
                                       label=label))
                    
                    f.data.setdefault('res.%s' % key, ' '.join([str(r['node_id']) for r in res]))
                    return True
                else:
                    return False
                            
            d=self.user.getAllBindedPlatformNodes(platform_id).addCallback(_cb)
            return d

        def addResources(ajobs, f):
            def _cb(r, g):
                if not [res for (b, res) in r if (b and res)]:
                    g.add(formal.Field('empty', 
                                       formal.String(immutable=True),
                                       formal.widgetFactory(formal.TextArea),
                                       label='Warning'))
                    f.data['res.empty']='None of the reserved resources are available in the testbed at the moment'
                f.add(g)
                
            if ajobs:
                self.ajobs=ajobs
                g=formal.Group('res', label='Available reserved resources')
                dl=[]
                for platform_id in self.ajobs[0]['resources']:
                    dl.append(addResourceField(f, g, platform_id))
                    d=defer.DeferredList(dl)
                d.addCallback(_cb, g)
                return d
            else:
                return defer.failure(ValueError('Empty active job list'))

        
        def addConfiguration(f):           
            g=formal.Group('ctrl', label='Job configuration')
            for index in range(1,4):
                addControlField(f, g, index)
            f.add(g)
            return f

        def _eb_form(flr):
            req=inevow.IRequest(ctx)
            req.setResponseCode(403)
            log.err('Error during jobs control form rendering for user %s:%s' % (self.user.username, flr.getErrorMessage().strip()))
            res = base.The404Page(self.user).renderHTTP(ctx)
            req.finishRequest(True)
            return res
        
        f=formal.Form()
        
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['job_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                pass
        
        if not self.id_list:
            req=inevow.IRequest(ctx)
            req.setResponseCode(403)
            log.err('Error during jobs control form rendering for user %s:%s' % (self.user.username, 'Empty job_id parameter'))
            res = base.The404Page(self.user).renderHTTP(ctx)
            req.finishRequest(True)
            return res
 
        f.addField('job_id', formal.Integer(), widgetFactory=formal.Hidden)
        f.data['job_id']=self.id_list[0]
             
        d=self.user.getListActiveJobs(self.id_list).addCallback(addResources, f)
        d.addCallback(lambda _: addConfiguration(f))
        d.addCallback(lambda _: addActionFields(f))
        d.addErrback(_eb_form)
        return d
    
    
    def acquireLock(self):
        try:
            if not self.lockobj.lock():
                raise formal.FormError(u'The testbed is currently in use by another user. Please try again a bit later...')
        except OSError:
            log.err('Error while acquiring the job control action lock!')
            raise formal.FormError(u'Problems acquiring the concurrency lock! Please try again a bit later...')
    
    def releaseLock(self):
        try:
            self.lockobj.unlock()
        except OSError, ValueError:
            log.err('Error while releasing the job control activity lock due to exception')

    def collectAndValidateReservedNodeSet(self, data):
        for platform_id in self.ajobs[0]['resources']:
            try:
                self.res_node_set |= set([int(id) for id in data['res.p%s' % platform_id].split()])
            except KeyError:
                pass
            except TypeError:
                self.releaseLock()
                raise formal.FieldValidationError(u'Reserved node list contains values that can not be converted to Integers')

    def collectAndValidateActionNodeSet(self, data):
        self.collectAndValidateReservedNodeSet(data)
        for index in range(1,4):
            
            field_name='ctrl.grp%s.nodes' % index
            data_field=data.get(field_name, '')
            try:
                if data_field is not None:
                    id_set = set([int(id) for id in data_field.strip().split()])
                else:
                    id_set = set()
            except TypeError:
                self.releaseLock()
                raise formal.FieldValidationError(u'Node list contains values that can not be converted to Integers', field_name)
                    
            if not id_set.issubset(self.res_node_set):
                self.releaseLock()
                raise formal.FieldValidationError(u'Node list contains non-reserved resources', field_name)
            else:
                self.act_node_set |= id_set
       
    def prepareOldBurnAction(self, data):
        
        self.acquireLock()
        self.collectAndValidateActionNodeSet(data)
        storagepath=lpath+'/'
        action=False

        for index in range(1,4):
            grp='ctrl.grp%s' % index
            nodes_key='%s.nodes' % grp
            image_key='%s.image' % grp
            sfversion_key='%s.sfversion' % grp
            sfspeed_key='%s.sfspeed' % grp
            channel_key='%s.channel' % grp
            nlist_file='%s%s%s' % (storagepath, nlist_name, index)
            ilist_file='%s%s%s' % (storagepath, ilist_name, index)

            try:
                os.remove(nlist_file)
                os.remove(ilist_file)
            except OSError:
                pass
            
            data_nodes=data.get(nodes_key, None)
            data_image=data.get(image_key, None)
            data_sfspeed= data.get(sfspeed_key, 0)
            data_sfversion=data.get(sfversion_key, 2)
            data_channel=data.get(channel_key, 26)
            
            if data_nodes is not None and data_nodes.strip():
                action=True
                try:
                    f=open(nlist_file, 'w')
                    f.write('%s SF%s %s C%s' % (data_nodes.strip(), 
                                                data_sfspeed, 
                                                data_sfversion, 
                                                data_channel))
                    f.close()
                    if data_image and data_image[1] is not None:
                        image_dst=open(ilist_file, 'w')
                        (t, image_src, n)=data_image
                        shutil.copyfileobj(image_src, image_dst)
                        image_dst.close()
                except IOError:
                    log.err('File error while setting up RPC command files')
                    self.releaseLock()
                    raise formal.FormError(u'Problems while setting up the RPC files! Please try again a bit later...')
        if not action:
            self.releaseLock()
        return action
    
    def prepareTracingAction(self, data):
        action=False
        self.acquireLock()
        self.collectAndValidateActionNodeSet(data)
        if self.act_node_set:
            action=True
        else:
            self.releaseLock()
        return action
    
    def refreshPage(self, data):
        u=url.here.clear()
        u=u.add('job_id', data['job_id'])
        return u
    
    def installAction(self, ctx, form, data):        
        if self.prepareOldBurnAction(data):
            return ControlJobActionPage(self.user, self.lockobj, 'install', data['job_id'])
        else:
            return self.refreshPage(data)
        
    def eraseAction(self, ctx, form, data):
        if self.prepareOldBurnAction(data):
            return ControlJobActionPage(self.user, self.lockobj, 'erase', data['job_id'])
        else:
            return self.refreshPage(data)
        
    def resetAction(self, ctx, form, data):
        if self.prepareOldBurnAction(data):
            return ControlJobActionPage(self.user, self.lockobj, 'reset', data['job_id'])
        else:
            return self.refreshPage(data)

    def powerOnAction(self, ctx, form, data):
        if self.prepareOldBurnAction(data):
            return ControlJobActionPage(self.user, self.lockobj, 'power_on', data['job_id'])
        else:
            return self.refreshPage(data)

    def powerOffAction(self, ctx, form, data):
        if self.prepareOldBurnAction(data):
            return ControlJobActionPage(self.user, self.lockobj, 'power_off',data['job_id'])
        else:
            return self.refreshPage(data)

    def startSFAction(self, ctx, form, data):
        if self.prepareOldBurnAction(data):
            return ControlJobActionPage(self.user, self.lockobj, 'start_sf',data['job_id'])
        else:
            return self.refreshPage(data)
    
    def stopSFAction(self, ctx, form, data):
        if self.prepareOldBurnAction(data):
            return ControlJobActionPage(self.user, self.lockobj, 'stop_sf', data['job_id'])
        else:
            return self.refreshPage(data)

    def startTracingAction(self, ctx, form, data):
        if self.prepareTracingAction(data):
            return ControlJobActionPage(self.user, self.lockobj, 'start_tracing', data['job_id'],
                                        self.ajobs[0]['time_end'], self.act_node_set)
        else:
            return self.refreshPage(data)
    
    def stopTracingAction(self, ctx, form, data):
        if self.prepareTracingAction(data):
            return ControlJobActionPage(self.user, self.lockobj, 'stop_tracing', data['job_id'], 
                                        self.ajobs[0]['time_end'], self.act_node_set)
        else:
            return self.refreshPage(data)


    def child_execute(self, ctx):
        return ControlJobActionPage(self.user, self.lockobj)

            
class ControlJobActionPage(base.AuthenticatedTwistPage):
    
    action_map={'install': 'Install',
                'erase': 'Erase',
                'reset': 'Reset',
                'power_on': 'Power up',
                'power_off': 'Power down',
                'start_sf': 'Start SF',
                'stop_sf': 'Stop SF',
                'start_tracing': 'Start Tracing',
                'stop_tracing': 'Stop Tracing'}
    
    def __init__(self, user, lockobj, action, job_id, time_end=None, act_node_set=set()):
        super(ControlJobActionPage, self).__init__(user)
        self.lockobj=lockobj
        self.action=action
        self.job_id=job_id
        self.time_end=time_end
        self.act_node_set=act_node_set
        self.started=False
    
    def releaseLock(self):
        try:
            self.lockobj.unlock()
        except OSError, ValueError:
            log.err('Error while releasing the job control activity lock due to exception')

 
    def beforeRender (self, ctx):
        super(ControlJobActionPage, self).beforeRender(ctx)
        ctx.fillSlots('action', self.action_map[self.action])

        def _cb(res):
            log.msg('Action page rendering finished cleanly')
        def _eb(flr):
            log.err('Action page rendering interrupted for user %s: %s , trying to remove the lock' % (self.user.username, flr.getErrorMessage().strip()))
            self.releaseLock()

        req = inevow.IRequest(ctx)
        d=req.notifyFinish()
        d.addCallbacks(_cb, _eb)
    
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Job Control ', T.slot(name='action'),' Action'],
                           T.h3['Execution log:'],
                           T.p(data=T.directive('action'), render=T.directive('output')),
                           T.div(render=T.directive('back_link'))                       
                       ]
#                   ]
               ]
    
    
    def data_action(self, ctx, data):

        def _cb(r):
            log.msg('Successful action %s for user %s' % (self.action, self.user.username))
            self.releaseLock()
            return r
        def _eb(f):
            log.err('Error during %s action for user %s:%s' % (self.action, self.user.username, f.getErrorMessage().strip()))
            self.releaseLock()
 
        if self.action in ('start_tracing', 'stop_tracing'):
            d=self.user.controlJobTracing(self.action, self.job_id, self.time_end, self.act_node_set)
        else:
            old_burn_act  = self.action_map[self.action]
            d=self.user.executeOldBurnAction(old_burn_act)
        
        d.addCallbacks(_cb,_eb)
        return d
            
    def render_output(self, ctx, data):
        if data:
            return ctx.tag[[T.br[l + "\n"] for l in data.splitlines()]]
        else:
            return ''
    
    def render_back_link(self, ctx, data):
        u=url.here.clear()
        u=u.add('job_id', self.job_id)
        return T.blockquote[T.a(href=u)['Back to the job control form.']]
