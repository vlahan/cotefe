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

from twisted.python import log
from nevow import inevow, tags as T, url

import formal
import base

# - Get all deployed supernodes according to the database
# - Issue bulk get on the switches to find the mac_addr/port mappings
# - Issue bulk get on the switches to the poe status MIB
# - combine the database information (on mac key) with the poe information
# - display the result on the page
# - try to cache the above info
# - users select items based on supernode_id
# - map the supernode_id to switch and port
# - issue snmp write on the proper MIB
# - Refresh button?



class SupernodeManagementPage(base.AuthenticatedTwistPage):
                
    def render_corefrag (self, ctx, data):
        return ctx.tag[T.div(id='primaryContent')[    
                           T.h2['Supernode Management'],
                           T.h3['Current status:'],
                           T.form(action=url.URL.fromContext(ctx).child('form_action'), method="post", class_='nevow-form', enctype='multipart/form-data')[
                               T.invisible(data=T.directive('supernodes'), render=T.directive('if'))[
                                   T.div(pattern='True')[
                                       T.table(render=T.directive('sequence'))[
                                           T.tr(pattern='header', render=T.directive('header')),
                                           T.tr(pattern='item', class_='rowA', render=T.directive('supernode_item')),
                                       ],
                                       T.span(render=T.directive('actions'), class_='actions'),
                                       T.script(language='javascript')['document.forms[0].action[0].focus();'],

                                    ],
                                    T.div(pattern='False')[
                                        T.p['''No supernodes were detected''',
                                            T.span(render=T.directive('back_link'))
                                        ]
                                    ]
                               ]
                           ]
                       ]
               ]


    def render_header(self, ctx, data):
        if self.user.role=='admin':
            return ctx.tag[T.th(width='5%')[''],
                           T.th(width='10%')['Supernode Id'],
                           T.th(width='10%')['Room'],
                           T.th(width='20%')['IP Address'], 
                           T.th(width='20%')['MAC Address'],
                           ]
        else:
            return ctx.tag[T.th(width='10%')['Supernode Id'],
                           T.th(width='20%')['IP Address'], 
                           T.th(width='20%')['MAC Address'],
                           ]
         
    def data_supernodes(self, ctx, data):
        return self.user.getAllSupernodes()         

    
    def render_supernode_item(self, ctx, supernode):

        if supernode['status'] == 'link_up':
             style='active'
        elif supernode['status'] == 'link_down':
             style='error'
        else:
            style='normal'
        
        if self.user.role=='admin':
            return ctx.tag[T.td(_class=style)[T.input(type='checkbox', name='id_%s' % supernode['supernode_id'], 
                                                  value='True')],
                           T.td(_class=style)[supernode['supernode_id']],
                           T.td(_class=style)[supernode['room']],
                           T.td(_class=style)[supernode['ip_addr']],
                           T.td(_class=style)[supernode['mac_addr']],
                           ]
        else:
            return ctx.tag[T.td(_class=style)[supernode['supernode_id']],
                           T.td(_class=style)[supernode['ip_addr']],
                           T.td(_class=style)[supernode['mac_addr']],
                           ]
            

    def render_actions(self, ctx, data):
        if self.user.role=='admin':
            return ctx.tag[T.input(type='submit', name='action', value='Enable'),
                           T.input(type='submit', name='action', value='Disable',),
                           T.input(type='submit', name='action', value='Refresh',),
                           ]
        else:
            return ctx.tag
            
    def child_form_action(self, ctx):
        req=inevow.IRequest(ctx)
        try:
            action=req.args['action'][0]
        except KeyError:
            action=None
        selection=[int(key.split('_')[1]) for key in req.args.keys() if (key.startswith('id') 
                                                                         and req.args[key][0]=='True')]

        if selection:
            if action=='Enable':
                u=url.here.sibling('enable').clear()
                for id in selection:
                    u=u.add('supernode_id', id)
                return u
            elif action=='Disable':
                u=url.here.sibling('disable').clear()
                for id in selection:
                    u=u.add('supernode_id', id)
                return u
            elif action=='Refresh':
                log.msg('Refresh: %s' % selection)
                return url.here.up()

        u=url.here.up()
        return u

    def child_enable(self, ctx):
        if self.user.role=='admin':
            return ControlSupernodePage(self.user, 'enable')

    def child_disable(self, ctx):
        if self.user.role=='admin':
            return ControlSupernodePage(self.user, 'disable')
 

class ControlSupernodePage(base.AuthenticatedTwistPage):
    
    def __init__(self, user, action):
        super(ControlSupernodePage, self).__init__(user)
        self.action=action
        self.id_list=[]
        
    def render_corefrag (self, ctx, data):
        return ctx.tag[T.div(id='primaryContent')[    
                           T.h2['Supernode Management'],
                           T.div(render=T.directive('title')),
                           T.invisible(data=T.directive('supernodes'), render=T.directive('if'))[
                               T.div(pattern='True')[
                                   T.table(render=T.directive('sequence'))[
                                       T.tr(pattern='header', render=T.directive('header')),
                                       T.tr(pattern='item', class_='rowA', render=T.directive('supernode_item')),
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
               ]

    def render_title(self, ctx, data):
        if self.action=='enable':
            return ctx.tag[T.h3['Enabling supernodes']]
        elif self.action=='disable':
            return ctx.tag[T.h3['Disabling supernodes']]
                           

    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='10%')['Supernode Id'],
                       T.th(width='10%')['Room'],
                       T.th(width='20%')['IP Address'], 
                       T.th(width='20%')['MAC Address'],
                       ]
         
    def data_supernodes(self, ctx, data):
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['supernode_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                return []
        if self.id_list:
            return self.user.getListSupernodes(self.id_list)
        else:
            return []
        
    def render_supernode_item(self, ctx, supernode):

        if supernode['status'] == 'link_up':
             style='active'
        elif supernode['status'] == 'link_down':
             style='error'
        else:
            style='normal'

        return ctx.tag[T.td(_class=style)[supernode['supernode_id']],
                       T.td(_class=style)[supernode['room']],
                       T.td(_class=style)[supernode['ip_addr']],
                       T.td(_class=style)[supernode['mac_addr']],
                       ]
    
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
            id_list_string=data['id_list']
            id_list=[int(id) for id in id_list_string]
            if id_list:
                return self.user.controlListSupernodes(id_list, self.action).addCallback(_cb)
            else:
                return url.here.up()
        except KeyError:
            return url.here.up()
    
    def cancel(self, ctx, form, data):
        u=url.here.up()
        return u

class DisableSupernodePage(base.AuthenticatedTwistPage):
    
    def __init__(self, user):
        super(DisableSupernodePage, self).__init__(user)
        self.id_list=[]
        
    def render_corefrag (self, ctx, data):
        return ctx.tag[T.div(id='primaryContent')[    
                           T.h2['Supernode Management'],
                           T.h3['Disabling supernodes:'],
                           T.invisible(data=T.directive('supernodes'), render=T.directive('if'))[
                               T.div(pattern='True')[
                                   T.table(render=T.directive('sequence'))[
                                       T.tr(pattern='header', render=T.directive('header')),
                                       T.tr(pattern='item', class_='rowA', render=T.directive('supernode_item')),
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
               ]


    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='10%')['Supernode Id'],
                       T.th(width='10%')['Room'],
                       T.th(width='20%')['IP Address'], 
                       T.th(width='20%')['MAC Address'],
                       ]
         
    def data_supernodes(self, ctx, data):
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['supernode_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                return []
        if self.id_list:
            return self.user.getListSupernodes(self.id_list)
        else:
            return []
        
    def render_supernode_item(self, ctx, supernode):

        if supernode['status'] == 'link_up':
             style='active'
        elif supernode['status'] == 'link_down':
             style='error'
        else:
            style='normal'

        return ctx.tag[T.td(_class=style)[supernode['supernode_id']],
                       T.td(_class=style)[supernode['room']],
                       T.td(_class=style)[supernode['ip_addr']],
                       T.td(_class=style)[supernode['mac_addr']],
                       ]
    
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
                return self.user.disableListSupernodes(id_list).addCallback(_cb)
            else:
                return url.here.up()
        except KeyError:
            return url.here.up()
    
    def cancel(self, ctx, form, data):
        u=url.here.up()
        return u
