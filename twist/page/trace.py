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
import time

from twisted.python import log, failure, threadable
from zope.interface import implements
from nevow import inevow, rend, tags as T, url

import formal
import base

def sizeof_fmt(num):
    for x in ['B','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

class JobTracesPage(base.AuthenticatedTwistPage):
    
    def __init__(self, user):
        super(JobTracesPage, self).__init__(user)
        self.job_id=None
                        
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Trace File Management'],
                           T.invisible(data=T.directive('jobs'), render=T.directive('if'))[
                               T.div(pattern='True')[
                                   T.h3['Job info:'],          
                                   T.table(render=T.directive('sequence'))[
                                       T.tr(pattern='header', render=T.directive('jobs_header')),
                                       T.tr(pattern='item', class_='rowA', render=T.directive('job_item')),
                                       T.tr(pattern='item', class_='rowB', render=T.directive('job_item')),
                                   ],
                               ],
                               T.div(pattern='False')[
                                   T.p['''You have insufficient rights for the operation or 
                                          you are trying to access a non-existing item.''',
                                          T.span(render=T.directive('back_link'))
                                   ],
                               ],
                           ],
                           T.invisible(data=T.directive('traces'), render=T.directive('if'))[
                               T.div(pattern='True')[
                                   T.form(action=url.URL.fromContext(ctx).child('form_action'), method="post", class_='nevow-form', enctype='multipart/form-data')[                       
                                       T.h3['Available traces:'],
                                               T.table(render=T.directive('sequence'))[
                                                   T.tr(pattern='header', render=T.directive('traces_header')),
                                                   T.tr(pattern='item', class_='rowA', render=T.directive('trace_item')),
                                                   T.tr(pattern='item', class_='rowB', render=T.directive('trace_item')),
                                               ],
                                               T.div(render=T.directive('actions'), class_='actions'),           
                                               T.script(language='javascript')['document.forms[0].action[0].focus();'],
                                   ],
                               ],
                               T.div(pattern='False')[
                                   T.blockquote['''There are no traces associated with this job.''']
                               ],
                           ],
                       ],
                   ]
#                ]

    def render_jobs_header(self, ctx, data):
        return ctx.tag[T.th(width='25%')['Description'],
                       T.th(width='25%')['Owner'], 
                       T.th(width='20%')['Resources'],
                       T.th(width='15%')['Start'], 
                       T.th(width='15%')['End'],
                       ]
         
    def data_jobs(self, ctx, data):
        if self.job_id is None:
            try:
                req=inevow.IRequest(ctx)
                job_id_list_string=req.args['job_id']
                self.job_id=int(job_id_list_string[0])
            except (KeyError, ValueError):
                return []
        if self.job_id is not None:
            return self.user.getListArchivedAndCurrentJobs([self.job_id])
        else:
            return []
        
    def render_job_item(self, ctx, job):
        if job['active']:
            style='active'
        else: style='normal'
        if job['user_id']==self.user.user_id:
            style="%s own" % style
        
        return ctx.tag[
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
    
    def render_traces_header(self, ctx, data):
        return ctx.tag[T.th(width='5%')[''],
                       T.th(width='35%')['Name'],
                       T.th(width='25%')['Date'], 
                       T.th(width='15%')['Size'],
                       ]
         
    def data_traces(self, ctx, data):
        if self.job_id is not None:        
            return self.user.getSingleJobAllTraces(self.job_id)
        else:
            return []
    
    def render_trace_item(self, ctx, trace):
        return ctx.tag[
                  T.td[T.input(type='checkbox', name='id:%s:%s' % (self.job_id, trace['name']), value='True')],
                  T.td[trace['name']],
                  T.td[time.ctime(trace['time'])],
                  T.td[sizeof_fmt(trace['size'])]
                ]
        
    def render_actions(self, ctx, data):
        return ctx.tag[T.input(type='submit', name='action', value='Download'),
                       T.input(type='submit', name='action', value='Delete'),
                ]
            
    def child_form_action(self, ctx):
        req=inevow.IRequest(ctx)
        try:
            action=req.args['action'][0]
        except KeyError:
            action=None
            
        selection = [(key.split(':')[1], key.split(':')[2]) for key in req.args.keys() if (key.startswith('id') and req.args[key][0]=='True')]
        if selection:
            if action=='Download':
                u=url.here.sibling('download').clear()
                job_id, trace_name = selection[0]
                u=u.add('job_id', job_id)

                u=u.add('trace_name', trace_name)
                return u
            elif action=='Delete':
                u=url.here.sibling('delete').clear()
                job_id, trace_name = selection[0]
                u=u.add('job_id', job_id)
                for job_id, trace_name in selection:
                    u=u.add('trace_name', trace_name)
                return u

        job_id_list = req.args['job_id']
        if job_id_list:
            u=url.here.up()
            u=u.add('job_id', job_id_list[0])
            return u
        else:
            u=url.parentdir().clear()
            return u
    
    def child_download(self, ctx):
        return TraceFileResource(self.user)

    def child_delete(self, ctx):
        return DeleteJobTracesPage(self.user)


class TraceFileResource(object):

    implements(inevow.IResource)

    contentTypes =  {
        '.txt': 'text/plain',
        '.gz' : 'application/x-gzip',
        '.bz2': 'application/x-bzip2'
        }

    contentEncodings = {
        '.txt': 'text/plain',
        '.gz' : 'application/x-gzip',
        '.bz2': 'application/x-bzip2'
        }

    def __init__(self, user):
        self.user=user
        self.job_id=None
        self.trace_name=None
        self.type=None
        self.encoding=None
   
    def locateChild(self, ctx, segments):
        return rend.NotFound
    
   
    def renderHTTP(self, ctx):

        req = inevow.IRequest(ctx)

        if req.method == 'HEAD':
            return ''

        try:
            job_id_list_string=req.args['job_id']
            self.job_id=int(job_id_list_string[0])
            self.trace_name=req.args['trace_name'][0]
        except (KeyError, IndexError, ValueError):
            return ErrorJobTracePage(self.user).renderHTTP(ctx)

        def _cb(rfilesize):
            rfile, rsize = rfilesize
            try:
                p, ext = os.path.splitext(self.trace_name)
                ext=ext.lower()
                self.type=self.contentTypes[ext]
                self.encoding=self.contentEncodings[ext]
            except (AttributeError, KeyError, ValueError):
                req.setHeader('content-type', 'text/plain')
                req.setHeader('content-encoding', 'text/plain')
                

            if self.type is not None:
                req.setHeader('content-type', self.type)
            if self.encoding is not None:
                req.setHeader('content-encoding', self.encoding)
                
            req.setHeader('accept-ranges','none')
            req.setHeader('content-disposition', 'attachment; filename="%s"' % self.trace_name)

            req.setHeader("content-length", str(rsize))
            rpacketsize=self.user.getTraceServerMaxPacketSize()
            log.msg('Started streaming trace file %s for user %s' % (self.trace_name, self.user.username))
            TraceFileTransfer(rfile, rsize, rpacketsize, req)
            return req.deferred

        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err('Error while streaming trace file: %s' % msg)
            return ErrorJobTracePage(self.user, msg).renderHTTP(ctx)
            
        return self.user.openTraceForReading(self.job_id, self.trace_name).addCallbacks(_cb, _eb)        

        
class TraceFileTransfer(object):

    req = None

    def __init__(self, rfile, size, rpacketsize, req):
        self.rfile = rfile
        self.size = size
        self.rpacketsize = rpacketsize
        self.written = 0
        self.req = req
        req.registerProducer(self, 0)

    def resumeProducing(self):
        if self.req is None:
            return
        
        def _cb(data):
            if data and self.req is not None:
                self.req.write(data)
                self.written+=len(data)
            if self.written==self.size:
                self.req.unregisterProducer()
                self.rfile.close()
                self.req.finish()
                self.req = None
                log.msg('Successfully finished streaming trace file')

        def _eb(f):
            log.err('Error while streaming trace file: %s' % f.getErrorMessage().strip())                
            self.req.unregisterProducer()
            self.req.finish()
            self.req = None
            self.rfile.close()
        
        d=self.rfile.readChunk(self.written, min(self.rpacketsize, self.size-self.written))
        d.addCallbacks(_cb, _eb)
        return d

    def pauseProducing(self):
        pass

    def stopProducing(self):
        self.req.unregisterProducer()        
        self.rfile.close()
        self.req.finish()        
        self.req = None
        log.msg('Stopped while streaming trace file')


    synchronized = ['resumeProducing', 'stopProducing']

threadable.synchronize(TraceFileTransfer)
            
class DeleteJobTracesPage(base.AuthenticatedTwistPage):
    
    def __init__(self, user):
        super(DeleteJobTracesPage, self).__init__(user)
        self.job_id=None
        self.trace_name_list=[]
        
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Trace File Management'],
                           T.h3['Deleting traces:'],
                           T.invisible(data=T.directive('traces'), render=T.directive('if'))[
                                   T.div(pattern='True')[
                                       T.h3['Traces to be deleted:'],
                                       T.table(render=T.directive('sequence'))[
                                           T.tr(pattern='header', render=T.directive('traces_header')),
                                           T.tr(pattern='item', class_='rowA', render=T.directive('trace_item')),
                                           T.tr(pattern='item', class_='rowB', render=T.directive('trace_item')),
                                       ],
                                       T.span(render=T.directive('form confirm')),
                                       T.script(language='javascript')['document.forms[0].cancel.focus();'],
                                   ],
                                   T.div(pattern='False')[
                                       T.blockquote['''No traces have been selected for removal''']
                                   ]
                           ],
                       ]
#                   ]
               ]

    def render_traces_header(self, ctx, data):
        return ctx.tag[
                   T.th(width='35%')['Name'],
                   T.th(width='25%')['Date'], 
                   T.th(width='15%')['Size'], 
               ]
         
    def data_traces(self, ctx, data):        
        if self.job_id is None:
            try:
                req=inevow.IRequest(ctx)
                job_id_list_string=req.args['job_id']
                self.job_id=int(job_id_list_string[0])
            except (KeyError, ValueError):
                return []
        if not self.trace_name_list:
            try:
                req=inevow.IRequest(ctx)
                self.trace_name_list=req.args['trace_name']
            except (KeyError, ValueError):
                return []
        if self.job_id is not None and self.trace_name_list:
            return self.user.getSingleJobListTraces(self.job_id, self.trace_name_list)
        else:
            return []
    
    def render_trace_item(self, ctx, trace):
        return ctx.tag[
                  T.td[trace['name']],
                  T.td[time.ctime(trace['time'])],
                  T.td[sizeof_fmt(trace['size'])]
                ]
        
    
    def form_confirm(self, ctx):
        f=formal.Form()
        f.addField('job_id', formal.Integer(), widgetFactory=formal.Hidden)
        f.addField('trace_name_list', formal.Sequence(required=True,type=formal.String()), widgetFactory=formal.Hidden)
        f.addAction(self.confirm, name='confirm', label='Confirm')
        f.addAction(self.cancel, name='cancel', label='Cancel', validate=False)
        f.data['job_id']=self.job_id
        f.data['trace_name_list']=self.trace_name_list
        return f
    
    def confirm(self, ctx, form, data):
        def _cb(result):
            u=url.here.up().clear()
            u=u.add('job_id', self.job_id)
            return u

        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err('Error while deleting trace file: %s' % msg)
            return ErrorJobTracePage(self.user, msg)
            
        try:
            self.job_id=data['job_id']    
            self.trace_name_list=data['trace_name_list']
            if self.job_id and self.trace_name_list:
                return self.user.deleteSingleJobListTraces(self.job_id, self.trace_name_list).addCallbacks(_cb, _eb)
            else:
                u=url.here.up().clear()
                u=u.add('job_id', self.job_id)
                return u
        except KeyError:
            u=url.parentdir().clear()
            return u
    
    def cancel(self, ctx, form, data):
        try:
            self.job_id=data['job_id']    
            self.trace_name_list=data['trace_name_list']
            u=url.here.up().clear()
            u=u.add('job_id', self.job_id)
            return u
        except KeyError:
            u=url.parentdir().clear()
            return u

class ErrorDeleteJobTracePage(base.AuthenticatedTwistPage):
    
    def __init__(self, user):
        super(ErrorDeleteJobTracePage, self).__init__(user)
 
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Trace File Management'],
                           T.h3['Error while deleting trace files:'],
                           T.div[
                               T.p['''You have insufficient rights for the operation or 
                                      you are trying to access a non-existing item.''',
                                   T.span(render=T.directive('back_link'))
                               ],
                           ],
                       ]
#                   ]
               ]
class ErrorJobTracePage(base.AuthenticatedTwistPage):
    
    def __init__(self, user, msg=None):
        super(ErrorJobTracePage, self).__init__(user)
        self.msg=msg
 
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Trace File Management'],
                           T.h3['Error during trace management operation:'],
                           T.div[
                               T.p(render=T.directive('errmsg')),
                               T.span(render=T.directive('back_link'))
                           ],
                       ]
#                   ]
               ]

    def render_errmsg(self, ctx, data):
        if self.msg is not None:
            try:
                msg=str(self.msg).split(':', 1)[1]
            except (ValueError, IndexError):
                msg=str(self.msg) 
            return ctx.tag[T.em[msg]]
        else:
            return ctx.tag[
                       T.em['''You have insufficient rights for the operation or 
                               you are trying to access a non-existing item.'''
                       ]
                   ]
