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

import datetime
from twisted.python import log
from nevow import inevow, tags as T, url

import formal
import base
import control
import trace
import cal

class JobsPage(base.AuthenticatedTwistPage):

    def __init__(self, user):
        super(JobsPage, self).__init__(user)
        self.period=datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.jobs=[]

    def beforeRender(self, ctx):
        super(JobsPage, self).beforeRender(ctx)
        req=inevow.IRequest(ctx)
        try:
            self.period=datetime.datetime(int(req.args['year'][0]), int(req.args['month'][0]), 1) 
        except (KeyError, IndexError, ValueError):
            pass
            
    def render_corefrag (self, ctx, data):
        return ctx.tag[
                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Job Management'],                      
                           T.form(action=url.URL.fromContext(ctx).child('form_action'), method="post", class_='nevow-form', enctype='multipart/form-data')[
                               T.h3['Scheduled jobs:'],
                               T.invisible(data=T.directive('jobs'), render=T.directive('if'))[
                                   T.div(pattern='True')[
                                       T.table(render=T.directive('sequence'))[
                                           T.tr(pattern='header', render=T.directive('header')),
                                           T.tr(pattern='item', class_='rowA', render=T.directive('job_item')),
                                           T.tr(pattern='item', class_='rowB', render=T.directive('job_item')),
                                       ]
                                   ],
                                   T.div(pattern='False')[
                                       T.blockquote['''There are no scheduled jobs in the selected time period.''']
                                   ]
                               ],
                               T.div(render=T.directive('actions'), class_='actions'),           
                               T.script(language='javascript')['document.forms[0].action[0].focus();'],
                           ]
                       ]
                   ],
                   T.div(id='secondaryContent')[
                       T.div(id='job_calendar')[
                           T.h3['Calendar'],
                           T.span(data=T.directive('caldata'), render=cal.cal),
                       ],
                       T.div(id='submenu')[
                            T.h3['Additional resources'],
                            T.ul(data=T.directive('submenu'), render=T.directive('sequence'))[
                                T.li(pattern='item', render=T.directive('menu_item')),
                            ]
                       ],

                   ]
                  
               ]
   
    def data_caldata(self, ctx, data):
        return self.period, self.jobs
    
    def data_submenu(self, ctx, data):
        return [('/jobs/archive', 'Archived Jobs')]
    
    def child_archive(self, ctx):
        return ArchivedJobsPage(self.user)

    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='5%')[''],
                       T.th(width='5%')['Id'],
                       T.th(width='20%')['Description'],
                       T.th(width='20%')['Owner'], 
                       T.th(width='20%')['Resources'],
                       T.th(width='15%')['Start'], 
                       T.th(width='15%')['End'],
                       ]
         
    def data_jobs(self, ctx, data):        
        def _cb(r):
            self.jobs=r
            return r
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err(msg)
            return []

        d=self.user.getAllMonthJobs(self.period)
        d.addCallbacks(_cb, _eb)
        return d
    
    def render_job_item(self, ctx, job):
        if job['active']:
            style='active'
        else: style='normal'
        if job['user_id']==self.user.user_id:
            style="%s own" % style
        return ctx.tag[
                  T.td(_class=style)[T.input(type='checkbox', name='id_%s' % job['job_id'], value='True')],
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

    def render_actions(self, ctx, data):
        return ctx.tag[T.input(type='submit', name='action', value='Add'),
                       T.input(type='submit', name='action', value='Edit'), 
                       T.input(type='submit', name='action', value='Delete'),
                       T.input(type='submit', name='action', value='Control'),
                       T.input(type='submit', name='action', value='Traces')
                ]
            
    def child_form_action(self, ctx):
        req=inevow.IRequest(ctx)
        try:
            self.period=datetime.datetime(int(req.args['year'][0]),int(req.args['month'][0]), 1) 
        except (KeyError, IndexError, ValueError):
            pass
        try:
            action=req.args['action'][0]
        except KeyError:
            action=None

        if action=='Add':
            u=url.here.sibling('add').clear()
            u=u.add('year', self.period.year)
            u=u.add('month',self.period.month)
            return u
        selection=[int(key.split('_')[1]) for key in req.args.keys() if (key.startswith('id') and req.args[key][0]=='True')]

        if selection:
            if action=='Edit':
                u=url.here.sibling('edit').clear()
                u=u.add('year', self.period.year)
                u=u.add('month',self.period.month)
                for id in selection:
                    u=u.add('job_id', id)
                return u
            elif action=='Delete':
                u=url.here.sibling('delete').clear()
#                u=u.add('year', self.period.year)
#                u=u.add('month',self.period.month)
                for id in selection:
                    u=u.add('job_id', id)
                return u
            elif action=='Control':
                u=url.here.sibling('control').clear()
#                u=u.add('year', self.period.year)
#                u=u.add('month',self.period.month)
                for id in selection:
                    u=u.add('job_id', id)
                return u
            elif action=='Traces':
                u=url.here.sibling('traces').clear()
                for id in selection:
                    u=u.add('job_id', id)
                return u


        u=url.here.up()
        u=u.remove('year')
        u=u.remove('month')
        u=u.add('year', self.period.year)
        u=u.add('month',self.period.month)
        return u
  
    
    def child_add(self, ctx):
        return AddJobPage(self.user)

    def child_edit(self, ctx):
        return EditJobPage(self.user)

    def child_delete(self, ctx):
        return DeleteJobsPage(self.user)

    def child_control(self, ctx):
        return control.ControlJobPage(self.user)

    def child_traces(self, ctx):
        return trace.JobTracesPage(self.user)

class ArchivedJobsPage(base.AuthenticatedTwistPage):

    def __init__(self, user):
        super(ArchivedJobsPage, self).__init__(user)
        self.period=datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.jobs=[]

    def beforeRender(self, ctx):
        super(ArchivedJobsPage, self).beforeRender(ctx)
        req=inevow.IRequest(ctx)
        try:
            self.period=datetime.datetime(int(req.args['year'][0]),int(req.args['month'][0]), 1) 
        except (KeyError, IndexError, ValueError):
            pass
            
    def render_corefrag (self, ctx, data):
        return ctx.tag[
                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Job Management'],                      
                           T.form(action=url.URL.fromContext(ctx).child('form_action'), method="post", class_='nevow-form', enctype='multipart/form-data')[
                               T.h3['Archived jobs:'],
                               T.invisible(data=T.directive('jobs'), render=T.directive('if'))[
                                   T.div(pattern='True')[
                                       T.table(render=T.directive('sequence'))[
                                           T.tr(pattern='header', render=T.directive('header')),
                                           T.tr(pattern='item', class_='rowA', render=T.directive('job_item')),
                                           T.tr(pattern='item', class_='rowB', render=T.directive('job_item')),
                                       ]
                                   ],
                                   T.div(pattern='False')[
                                       T.blockquote['''There are no archived jobs in the selected time period.''']
                                   ]
                               ],
                               T.div(render=T.directive('actions'), class_='actions'),           
                               T.script(language='javascript')['document.forms[0].action[0].focus();'],
                           ]
                       ]
                   ],
                   T.div(id='secondaryContent')[
                       T.div(id='job_calendar')[
                           T.h3['Calendar'],
                           T.span(data=T.directive('caldata'), render=cal.cal),
                       ],
                       T.div(id='submenu')[
                            T.h3['Additional resources'],
                            T.ul(data=T.directive('submenu'), render=T.directive('sequence'))[
                                T.li(pattern='item', render=T.directive('menu_item')),
                            ]
                       ],

                   ]
                  
               ]
 
 
    def data_caldata(self, ctx, data):
        return self.period, self.jobs
    
    def data_submenu(self, ctx, data):
        return [('/jobs', 'Active Jobs')]

    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='5%')[''],
                       T.th(width='5%')['Id'],
                       T.th(width='20%')['Description'],
                       T.th(width='20%')['Owner'], 
                       T.th(width='20%')['Resources'],
                       T.th(width='15%')['Start'], 
                       T.th(width='15%')['End'],
                       ]
         
    def data_jobs(self, ctx, data):
        def _cb(r):
            self.jobs=r
            return r
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err(msg)
            return []

        d=self.user.getAllArchivedMonthJobs(self.period)
        d.addCallbacks(_cb, _eb)
        return d
    
    def render_job_item(self, ctx, job):
        style='normal'
        if job['user_id']==self.user.user_id:
            style="%s own" % style
        return ctx.tag[
                  T.td(_class=style)[T.input(type='checkbox', name='id_%s' % job['job_id'], value='True')],
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

    def render_actions(self, ctx, data):
        if self.user.role=='admin':            
            return ctx.tag[
                       T.input(type='submit', name='action', value='Refresh'),
                       T.input(type='submit', name='action', value='Purge'),
                       T.input(type='submit', name='action', value='Traces')
                   ]
        else:
            return ctx.tag[
                       T.input(type='submit', name='action', value='Traces')
                   ]

    
    def prepareReturnURL(self, ctx):
        u=url.here.up()
        u=u.remove('year')
        u=u.remove('month')
        u=u.add('year', self.period.year)
        u=u.add('month',self.period.month)
        return u
        
    def child_form_action(self, ctx):
        def _cb(r):
            return self.prepareReturnURL(ctx)
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err(msg)
            return self.prepareReturnURL(ctx)
        
        req=inevow.IRequest(ctx)
        try:
            self.year=int(req.args['year'][0])
            self.month=int(req.args['month'][0])
        except (KeyError, IndexError, ValueError):
            pass
     
        try:
            action=req.args['action'][0]
        except KeyError:
            action=None
 
        selection=[int(key.split('_')[1]) for key in req.args.keys() if (key.startswith('id') and req.args[key][0]=='True')]

        if action=='Refresh':
            d=self.user.refreshAllArchivedJobs()
            d.addCallbacks(_cb, _eb)
            return d

        if selection:
            if action=='Purge':
                u=url.here.sibling('purge').clear()
                for id in selection:
                    u=u.add('job_id', id)
                return u
            elif action=='Traces':
                u=url.here.sibling('traces').clear()
                for id in selection:
                    u=u.add('job_id', id)
                return u

        u=url.here.up()
        u=u.remove('year')
        u=u.remove('month')
        u=u.add('year', self.period.year)
        u=u.add('month',self.period.month)
        return u

    def child_purge(self, ctx):
        return PurgeArchivedJobsPage(self.user)

    def child_traces(self, ctx):
        return trace.JobTracesPage(self.user)

class PurgeArchivedJobsPage(base.AuthenticatedTwistPage):
    
    def __init__(self, user):
        super(PurgeArchivedJobsPage, self).__init__(user)
        self.id_list=[]
        
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Job Management'],
                           T.h3['Purging archived jobs:'],
                           T.invisible(data=T.directive('jobs'), render=T.directive('if'))[
                               T.div(pattern='True')[
                                   T.table(render=T.directive('sequence'))[
                                       T.tr(pattern='header', render=T.directive('header')),
                                       T.tr(pattern='item', class_='rowA', render=T.directive('job_item')),
                                       T.tr(pattern='item', class_='rowB', render=T.directive('job_item')),
                                   ],
                                   T.span(render=T.directive('form confirm')),
                                   T.script(language='javascript')['document.forms[0].cancel.focus();'],

                                ],
                                T.div(pattern='False')[
                                    T.p['''You have insufficient rights for the operation or 
                                           you are trying to delete a non-existing item.''',
                                        T.span(render=T.directive('back_link'))
                                    ]
                                ]
                           ]
                       ]
#                   ]
               ]

    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='10%')['Id'],
                       T.th(width='20%')['Description'],
                       T.th(width='20%')['Owner'], 
                       T.th(width='20%')['Resources'],
                       T.th(width='15%')['Start'], 
                       T.th(width='15%')['End'],
                       ]
         
    def data_jobs(self, ctx, data):
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['job_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                return []
        if self.id_list:
            return self.user.getListArchivedJobs(self.id_list)
        else:
            return []
        
    def render_job_item(self, ctx, job):
        style='normal'
        if job['user_id']==self.user.user_id:
            style="%s own" % style
        
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
    
    def form_confirm(self, ctx):
        f=formal.Form()
        f.addField('id_list', formal.Sequence(required=True,type=formal.Integer()), widgetFactory=formal.Hidden)
        f.addAction(self.confirm, name='confirm', label='Confirm')
        f.addAction(self.cancel, name='cancel', label='Cancel', validate=False)
        f.data['id_list']=self.id_list
        return f
    
    def confirm(self, ctx, form, data):
        def _cb(result):
            return url.here.up()

        try:    
            id_list=data['id_list']
            if id_list:
                return self.user.purgeListArchivedJobs(id_list).addCallback(_cb)
            else:
                return url.here.up()
        except KeyError:
            return url.here.up()
    
    def cancel(self, ctx, form, data):
        return url.here.up()




    
class DeleteJobsPage(base.AuthenticatedTwistPage):
    
    def __init__(self, user):
        super(DeleteJobsPage, self).__init__(user)
        self.id_list=[]
        
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Job Management'],
                           T.h3['Deleting jobs:'],
                           T.invisible(data=T.directive('jobs'), render=T.directive('if'))[
                               T.div(pattern='True')[
                                   T.table(render=T.directive('sequence'))[
                                       T.tr(pattern='header', render=T.directive('header')),
                                       T.tr(pattern='item', class_='rowA', render=T.directive('job_item')),
                                       T.tr(pattern='item', class_='rowB', render=T.directive('job_item')),
                                   ],
                                   T.span(render=T.directive('form confirm')),
                                   T.script(language='javascript')['document.forms[0].cancel.focus();'],

                                ],
                                T.div(pattern='False')[
                                    T.p['''You have insufficient rights for the operation or 
                                           you are trying to delete a non-existing item.''',
                                        T.span(render=T.directive('back_link'))
                                    ]
                                ]
                           ]
                       ]
#                   ]
               ]

    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='10%')['Id'],
                       T.th(width='20%')['Description'],
                       T.th(width='20%')['Owner'], 
                       T.th(width='20%')['Resources'],
                       T.th(width='15%')['Start'], 
                       T.th(width='15%')['End'],
                       ]
         
    def data_jobs(self, ctx, data):
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['job_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                return []
        if self.id_list:
            return self.user.getListJobs(self.id_list)
        else:
            return []
        
    def render_job_item(self, ctx, job):
        if job['active']:
            style='active'
        else: style='normal'
        if job['user_id']==self.user.user_id:
            style="%s own" % style
        
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
    
    def form_confirm(self, ctx):
        f=formal.Form()
        f.addField('id_list', formal.Sequence(required=True,type=formal.Integer()), widgetFactory=formal.Hidden)
        f.addAction(self.confirm, name='confirm', label='Confirm')
        f.addAction(self.cancel, name='cancel', label='Cancel', validate=False)
        f.data['id_list']=self.id_list
        return f
    
    def confirm(self, ctx, form, data):
        def _cb(result):
            return url.here.up()

        try:    
            id_list=data['id_list']
            if id_list:
                return self.user.deleteListJobs(id_list).addCallback(_cb)
            else:
                return url.here.up()
        except KeyError:
            return url.here.up()
    
    def cancel(self, ctx, form, data):
        u=url.here.up()
        return u
    
class AddJobPage(base.AuthenticatedTwistPage):
    
    def __init__(self, user, id_list=[]):
        super(AddJobPage, self).__init__(user)
        self.cid_list=[]
        self.period=datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.jobs=[]

    def beforeRender(self, ctx):
        super(AddJobPage, self).beforeRender(ctx)
        req=inevow.IRequest(ctx)
        try:
            self.period=datetime.datetime(int(req.args['year'][0]),int(req.args['month'][0]), 1)
        except (KeyError, IndexError, ValueError):
            pass
    
    def render_corefrag (self, ctx, data):
        return ctx.tag[
                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Job Management'],
                           T.h3['Adding a new job:'],
                           T.invisible(data=T.directive('cjobs'), render=T.directive('if'))[
                               T.div(pattern='True', _class='errors')[
                                   T.p[T.b['Conflicting jobs']],
                                   T.table(render=T.directive('sequence'))[
                                       T.tr(pattern='header', render=T.directive('header')),
                                       T.tr(pattern='item', class_='rowA', render=T.directive('cjob_item')),
                                       T.tr(pattern='item', class_='rowB', render=T.directive('cjob_item')),
                                   ],
                               ],
                               T.div(pattern='False')[T.invisible()]
                            ],
                            T.div(render=T.directive('form addJob')),
                            T.script(language='javascript')['document.forms[0].resources[0].focus();'],
                       ]
                   ],
                   T.div(id='secondaryContent')[
                       T.div(id='job_calendar')[
                           T.h3['Calendar'],
                           T.span(data=T.directive('caldata'), render=cal.cal),
                       ],

                   ]

               ]
    
    def data_caldata(self, ctx, data):
        def _cb(r):
            self.jobs=r
            return self.period, self.jobs
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err(msg)
            return self.period, []
        
        d=self.user.getAllMonthJobs(self.period)
        d.addCallbacks(_cb, _eb)
        return d
    
    def data_cjobs(self, ctx, data):
        if self.cid_list:
            return self.user.getListAllJobs(self.cid_list)
        else:
            return []
        
    def render_header(self, ctx, data):
        return ctx.tag[
                       T.th(width='10%')['Id'],
                       T.th(width='20%')['Description'],
                       T.th(width='20%')['Owner'], 
                       T.th(width='20%')['Resources'],
                       T.th(width='15%')['Start'], 
                       T.th(width='15%')['End'],
                       ]
         
        
    def render_cjob_item(self, ctx, job):
        style='errors'
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
    
    def form_addJob(self, ctx):

        now = datetime.datetime.now()
        if self.period.year != now.year or self.period.month != now.month:
            begin=self.period
            offset=datetime.timedelta(hours=12)
        else:
            begin=now
            offset=datetime.timedelta(hours=1)
            
        duration=datetime.timedelta(hours=2)
        
        begin=begin+offset
        
        begin=begin.replace(minute=0, second=0, microsecond=0)
        begin_date=begin.date()
        begin_time=begin.time()
        
        
        end=begin+duration
        end_date=end.date()
        end_time=end.time()
        
        
        yearFrom=begin.year
        yearTo=yearFrom+5
        
        platformOptions=[(1,'eyesIFX v2.1'),
                         (2, 'eyesIFX v2.0'), 
                         (3, 'TelosA'),
                         (4, 'TelosB'),
                         (5, 'Tmote')]
        f=formal.Form()
        
        f.addField('resources', 
                   formal.Sequence(required=True,type=formal.Integer()),
                   formal.widgetFactory(formal.CheckboxMultiChoice, 
                                        options=platformOptions),
                   label='Platforms')
                                                
                                                
        f.addField('time_begin_date', formal.Date(required=True),
                                             formal.widgetFactory(formal.DatePartsSelect, 
                                                                  dayFirst=True,
                                                                  yearFrom=yearFrom,
                                                                  yearTo=yearTo),
                                             label='Start date')
        f.addField('time_begin_time', formal.Time(required=True),
                                             label='Start time')
        
        f.addField('time_end_date', formal.Date(required=True),
                                             formal.widgetFactory(formal.DatePartsSelect, 
                                                                  dayFirst=True,
                                                                  yearFrom=yearFrom,
                                                                  yearTo=yearTo),
                                             label='End date')
        f.addField('time_end_time', formal.Time(required=True),
                                             label='End time')
 
        f.addField('description',
                   formal.String(required=True, 
                                 validators=[formal.LengthValidator(max=300)]),
                   formal.widgetFactory(formal.TextArea),
                   label='Description')
       
        f.addAction(self.addSingleJob, label='Add')
        f.addAction(self.cancel, name='cancel', label='Cancel', validate=False)
        
        f.data={'time_begin_date': begin_date, 
                'time_begin_time': begin_time,
                'time_end_date': end_date, 
                'time_end_time': end_time,
                'description': 'Add job description here...'
                }
                
        
        return f

    def addSingleJob(self, ctx, form, data):
        def _cb(result):
            u=url.here.up()
            u=u.remove('year')
            u=u.remove('month')
            u=u.add('year', data['time_begin_date'].year)
            u=u.add('month',data['time_begin_date'].month)
            return u
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err(msg)
            if msg.startswith('TwistDBException:'):
                if 'conflicts' in msg:
                    c_job_match=base.job_re.match(msg)
                    self.cid_list=[int(c_job_match.group('job_id'))]
                    raise formal.FormError(c_job_match.group('msg'))
                else:
                    raise formal.FormError(msg[17:])
            else:
                log.err(f.getTraceback())
                return url.here.up()
        
        time_begin=datetime.datetime.combine(data['time_begin_date'], data['time_begin_time'])
        self.period=time_begin.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        time_end=datetime.datetime.combine(data['time_end_date'], data['time_end_time'])

        #validation
        if time_begin<=datetime.datetime.now():
            raise formal.FieldValidationError(u'Job start time has to be in the future.', fieldName='time_begin_time')
        if time_end <= time_begin:
            raise formal.FieldValidationError(u'Job end time has to be later than start time.', fieldName='time_end_time') 
        data['time_begin']=time_begin
        data['time_end']=time_end

        return self.user.addSingleJob(data).addCallbacks(_cb, _eb)
    
    def cancel(self, ctx, form, data):
        return url.here.up()

class EditJobPage(base.AuthenticatedTwistPage):
    
    def __init__(self, user):
        super(EditJobPage, self).__init__(user)
        self.id_list=[]
        self.cid_list=[]
        self.period=datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.jobs=[]

    def beforeRender(self, ctx):
        super(EditJobPage, self).beforeRender(ctx)
        req=inevow.IRequest(ctx)
        try:
            self.period=datetime.datetime(int(req.args['year'][0]),int(req.args['month'][0]), 1) 
        except (KeyError, IndexError, ValueError):
            pass
    
    def render_corefrag (self, ctx, data):
        return ctx.tag[
                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Job Management'],
                           T.h3['Editing job info:'],                           
                           T.invisible(data=T.directive('cjobs'), render=T.directive('if'))[
                               T.div(pattern='True', _class='errors')[
                                   T.p[T.b['Conflicting jobs']],
                                       T.table(render=T.directive('sequence'))[
                                           T.tr(pattern='header', render=T.directive('header')),
                                           T.tr(pattern='item', class_='rowA', render=T.directive('cjob_item')),
                                           T.tr(pattern='item', class_='rowB', render=T.directive('cjob_item')),
                                       ],
                                   ],
                               T.div(pattern='False')[T.invisible()]
                           ],
                           T.invisible(data=T.directive('jobs'), render=T.directive('if'))[
                               T.div(pattern='True', render=T.directive('form editJob')),
                               T.div(pattern='False')[
                                   T.p['''You have insufficient rights for the operation or 
                                          you are trying to edit a non-existing item.''',
                                          T.span(render=T.directive('back_link'))
                                   ]
                               ]
                           ]
                       ]
                   ],
                   T.div(id='secondaryContent')[
                       T.div(id='job_calendar')[
                           T.h3['Calendar'],
                           T.span(data=T.directive('caldata'), render=cal.cal),
                       ],

                   ]

               ]
    
    def data_caldata(self, ctx, data):
        def _cb(r):
            self.jobs=r
            return self.period, self.jobs
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err(msg)
            return self.period, self.jobs

        d=self.user.getAllMonthJobs(self.period)
        d.addCallbacks(_cb, _eb)
        return d
    
    def data_cjobs(self, ctx, data):
        if self.cid_list:
            return self.user.getListAllJobs(self.cid_list) # list all conflicting jobs (even not owned by the user)
        else:
            return []
        
    
    def data_jobs(self, ctx, data):
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['job_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                return []
        if self.id_list:
            def _cb(r):
                if r:
                    self.period.replace(year=r[0]['time_begin'].year, month=r[0]['time_begin'].month)
                return r
            d=self.user.getListJobs(self.id_list)
            d.addCallback(_cb)
            return d
        else:
            return []    
    
    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='10%')['Id'],
                       T.th(width='20%')['Description'],
                       T.th(width='20%')['Owner'], 
                       T.th(width='20%')['Resources'],
                       T.th(width='15%')['Start'], 
                       T.th(width='15%')['End'],
                       ]
         
        
    def render_cjob_item(self, ctx, job):
        style='errors'
        
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
    
    def form_editJob(self, ctx):

        now=datetime.datetime.now()
            
        offset=datetime.timedelta(hours=1)
        duration=datetime.timedelta(hours=2)
        
        begin=now+offset        
        begin=begin.replace(minute=0, second=0, microsecond=0)

        begin_date=begin.date()
        begin_time=begin.time()
        
        
        end=begin+duration
        end_date=end.date()
        end_time=end.time()
        
        
        yearFrom=begin.year
        yearTo=yearFrom+5

        platformOptions=[(1,'eyesIFX v2.1'),
                         (2, 'eyesIFX v2.0'), 
                         (3, 'TelosA'),
                         (4, 'TelosB'),
                         (5, 'Tmote')]
        
        
        f=formal.Form()

        f.addField('job_id', formal.Integer(), widgetFactory=formal.Hidden)

        f.addField('resources', 
                   formal.Sequence(required=True,type=formal.Integer()),
                   formal.widgetFactory(formal.CheckboxMultiChoice, 
                                        options=platformOptions),
                   label='Platforms')
                                                
                                                
        f.addField('time_begin_date', formal.Date(required=True),
                                             formal.widgetFactory(formal.DatePartsSelect,
                                                                  dayFirst=True,
                                                                  yearFrom=yearFrom,
                                                                  yearTo=yearTo),
                                             label='Start date')
        f.addField('time_begin_time', formal.Time(required=True),
#                                             formal.widgetFactory(formal.MultiselectChoice),
                                             label='Start time')
        
        f.addField('time_end_date', formal.Date(required=True),
                                             formal.widgetFactory(formal.DatePartsSelect, 
                                                                  dayFirst=True,
                                                                  yearFrom=yearFrom,
                                                                  yearTo=yearTo),
                                             label='End date')
        f.addField('time_end_time', formal.Time(required=True),
#                                             formal.widgetFactory(formal.MultiselectChoice),
                                             label='End time')
 
        f.addField('description',
                   formal.String(required=True, 
                                 validators=[formal.LengthValidator(max=300)]),
                   formal.widgetFactory(formal.TextArea),
                   label='Description')

        f.addAction(self.updateSingleJob, label='Update')
        f.addAction(self.cancel, name='cancel', label='Cancel', validate=False)
        
        

        def _cb(data, f):        
            def pack_data(original):
                f.data={'job_id': self.id_list[0],
                        'resources':original['resources'],
                        'time_begin_date': original['time_begin'].date(), 
                        'time_begin_time': original['time_begin'].time(),
                        'time_end_date': original['time_end'].date(), 
                        'time_end_time': original['time_end'].time(),
                        'description': original['description'],
                        'active': original['active']
                        }

            if data and data[0]['job_id']==self.id_list[0]:
                pack_data(data[0])
                if f.data['active']:
                    f.getItemByName('time_begin_date').type.immutable=True
                    f.getItemByName('time_begin_time').type.immutable=True
                    
            else:
                f.data={}            
            return f
        
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['job_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                pass
        
        if self.id_list:
            d=self.user.getSingleJob(self.id_list[0])
            d.addCallback(_cb, f)
            return d
        else:
            return f

    def updateSingleJob(self, ctx, form, data):
        
        try:
            job_id=data['job_id']
        except KeyError:
            raise formal.FormError('Insufficient permissions or editing a non-existing job!')
 
        self.id_list=[job_id]

        def _cb(result):
            u=url.here.up()
            u=u.remove('year')
            u=u.remove('month')
            u=u.add('year', data['time_begin_date'].year)
            u=u.add('month',data['time_begin_date'].month)
            return u
        def _eb(f):
            msg=f.getErrorMessage().strip()
            log.err(msg)
            if msg.startswith('TwistDBException:'):
                if 'conflicts' in msg:
                    try:
                        c_job_match=base.job_re.match(msg)
                        self.cid_list=[int(c_job_match.group('job_id'))]
                        raise formal.FormError(c_job_match.group('msg'))
                    except AttributeError:
                        pass
                raise formal.FormError(msg[17:])
            else:
                log.err('%s:%s' % (f.getErrorMessage(), f.getTraceback()))
                return url.here.up()

            log.err('Error during updating job.')
            return url.here.up()
        
        time_begin=datetime.datetime.combine(data['time_begin_date'], data['time_begin_time'])
        self.period=time_begin.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        time_end=datetime.datetime.combine(data['time_end_date'], data['time_end_time'])
       
        #validation
        if time_end <= time_begin:
            raise formal.FieldValidationError(u'Job end time has to be later than start time.', fieldName='time_end_time') 

        data['time_begin']=time_begin
        data['time_end']=time_end
        
        return self.user.updateSingleJob(job_id, data).addCallbacks(_cb, _eb)
    
    def cancel(self, ctx, form, data):
        return url.here.up()

