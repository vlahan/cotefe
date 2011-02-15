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

from twisted.python import log, failure
from zope.interface import implements
from nevow import inevow, tags as T, url, guard
import formal

import base
import textcha

class LogInPage(base.TwistPage):
        
    def render_corefrag (self, ctx, data):
        req = inevow.IRequest(ctx)        
        try:
            uTo=req.args['urlTo'][0]
            login_path=url.URL.fromString(uTo)
            login_path.pathList(copy=False).insert(0, guard.LOGIN_AVATAR)
        except (KeyError, IndexError):
            login_path = url.root.clear().child(guard.LOGIN_AVATAR).child('')
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Sign in to TWIST'],
                           T.form(action=login_path, method='post', class_='nevow-form')[
                               T.div(data=T.directive('loginerror'), render=T.directive('loginerror')),                                                                                                                
                               T.div(class_='field string textinput required')[
                                   T.label(class_='label')['Username'],
                                   T.input(class_='input', type='text',name='username')
                               ],
                               T.div(class_='field string password required')[
                                   T.label(class_='label')['Password'],
                                   T.input(class_='input', type='password',name='password'),
                               ],
                               T.div(_class='actions')[
                                   T.input(type='submit', name='commit', value='Sign in')
                               ]
                           ],
                           T.script(language='javascript')['document.forms[0].username.focus();'],
                       ],
#                   ],
               ]
    
    def data_loginerror(self, ctx, data):
        req = inevow.IRequest(ctx)
        return req.args.get('login-failure', '')
        
    def render_loginerror(self, ctx, error):
        if error:     
            return T.p(_class='errors')[error[0], ' Please try again...']
        else:
            return ''
            

class RequestAccountPage(base.TwistPage):
        
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Request a new account'],
                           T.div(render=T.directive('form requestAccount')),
                           T.script(language='javascript')['document.forms[0].first_name.focus();'],
                           T.br(),
                           T.div[
                               T.blockquote[
                                   T.i['Note:'], T.br(),
				      'Please follow the procedure outlined in the ', T.a(href='http://www.twist.tu-berlin.de/wiki/TWIST/Instances/TKN/TermsOfUse')['Terms of Use'],
                                      ' document to complete the account request process.', T.br(),
                                      'You will be notified by email once the activation is completed.'
                               ]
                           ]
                        ]
 #                   ]
                ]
    
    def form_requestAccount(self, ctx):
        f=formal.Form()
        f.addField('first_name', formal.String(required=True, validators=[formal.LengthValidator(max=20)]), label='First Name')
        f.addField('last_name', formal.String(required=True, validators=[formal.LengthValidator(max=20)]), label='Last Name')
        f.addField('email', formal.String(required=True, validators=[formal.LengthValidator(max=50),
                                                                     formal.PatternValidator(r'.+@[a-zA-Z\.\-]+')]), label='Email')
        f.addField('username', formal.String(required=True,validators=[formal.LengthValidator(min=6),
                                                                          formal.PatternValidator(r'^[a-zA-Z_\-0-9]*$'),
                                                                          UsernameValidator(ctx),]),
                                                label='Choose a username')
        f.addField('passwd', formal.String(required=True, validators=[formal.LengthValidator(min=8)]),
                                                                         formal.widgetFactory(formal.CheckedPassword), 
                                                label='Choose a password')
        if self.user.textcha.enabled:
            f.addField('textcha_q', formal.String(immutable=True, required=True), 
                                    formal.widgetFactory(formal.TextArea), 
                                    label='Spam control question')
            f.addField('textcha_a', formal.String(required=True, 
                                                  validators=[textcha.TextChaValidator(self.user.textcha)]),
                                    label='Answer')
            f.data['textcha_q']=self.user.textcha.question
        f.addAction(self.requestAccount, label='Request')
        return f

    def requestAccount(self, ctx, form, data):
        def _cb(r):
            return RequestAccountSuccessfulPage(self.user)
        def _eb(f):
            log.err('Error during requesting a new account.')
            return base.ErrorPage(self.user)
        d=self.user.requestAccount(data)
        d.addCallbacks(_cb, _eb)
        return d

class RequestAccountSuccessfulPage(base.TwistPage):
    
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Successful account request'],
                           T.div[
                                 T.blockquote[
                                     T.i['Note:'], T.br(),
                                     'Your account request has been noted.', T.br(),
                                     'You will be notified by email when the procedure is completed.'],
                           ],
                           T.div[T.a(href='/')['Back to the top page...']]
                       ]
#                   ]
               ]
        
class UsernameValidator(object):
    implements(formal.iformal.IValidator)
    
    def __init__(self, ctx):
        self.ctx=ctx
        
    def validate(self, field, value):
        def _cb(r):
            if r:
                raise formal.FieldValidationError(u'The chosen username is already taken.')  
        def _eb(f):
            raise formal.FieldValidationError(u'Error during field validation')
        d=self.ctx.tag.user.checkUsernameExists(value)
        d.addCallbacks(_cb, _eb)
        return d

class MyInfoPage(base.AuthenticatedTwistPage):
        
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                       T.h2['My Info Management'],
                       T.h3['My info:'],
                           T.table(data=T.directive('users'), render=T.directive('sequence'))[
                               T.tr(pattern='header', render=T.directive('header')),
                               T.tr(pattern='item', class_='rowA', render=T.directive('user')),
                           ],
                           T.div[T.directive('form myInfo')],
                           T.script(language='javascript')['document.forms[0].first_name.focus();'],
                       ]
#                   ]
               ]

    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='10%')['Username'], 
                       T.th(width='25%')['First Name'], 
                       T.th(width='25%')['Last Name'],
                       T.th(width='30%')['Email'],
                       T.th(width='10%')['Role'],
                       ]
         
    def data_users(self, ctx, data):
        return self.user.getSingleUser(self.user.user_id)
    
    
    def render_user(self, ctx, user):
        style='active'
        return ctx.tag[ T.td(_class=style)[user['username']],
                       T.td(_class=style)[user['first_name']],
                       T.td(_class=style)[user['last_name']],
                       T.td(_class=style)[user['email']],
                       T.td(_class=style)[user['role']],
                       ]

    def form_myInfo(self, ctx):
        f=formal.Form()
        f.addField('first_name', formal.String(required=True, validators=[formal.LengthValidator(max=20)]), label='First Name')
        f.addField('last_name', formal.String(required=True, validators=[formal.LengthValidator(max=20)]), label='Last Name')
        f.addField('email', formal.String(immutable=True), label='Email')
        f.addField('username', formal.String(immutable=True), label='Username')
        f.addField('passwd', formal.String(required=False, validators=[formal.LengthValidator(min=8)]),
                                                                         formal.widgetFactory(formal.CheckedPassword), 
                                                label='New Password', description='Leave blank to retain the old password')
        f.addField('role', formal.String(immutable=True), label='Role')
        

        f.addAction(self.updateSingleUser, label='Update')
        f.addAction(self.deleteSingleUser, name='remove', label='Remove', validate=False)
        
        def _cb(data, f):
            if data:
                f.data=data[0]
                return f
            else:
                f.data={}
                return f
        def _eb(f):
            log.err('Error during fetching user data: %s' % f.getErrorMessage())
            return []
        d=self.user.getSingleUser(self.user.user_id).addCallback(_cb, f).addErrback(_eb)
        return d

    def updateSingleUser(self, ctx, form, data):
        def _eb(f):
            log.err('Error during updating user.')
        return self.user.updateSingleUser(self.user.user_id, data).addErrback(_eb)

    def deleteSingleUser(self, ctx, form, data):
        return url.here.child('confirm').clear()

    def child_confirm(self, ctx):
        return ConfirmAccountRemovalPage(self.user)
 
 
class ConfirmAccountRemovalPage(base.AuthenticatedTwistPage):
            
    def render_corefrag (self, ctx, data):
        return ctx.tag[
                        T.div(id='primarycontent')[
                            T.h2['Confirm action:'],
                            T.div(id='content')[
                                T.div[
                                      T.blockquote[
                                          T.i['Warning:'], 
                                          T.br(),
                                          '''Are sure that you want to permanently delete your
                                             account including all registered jobs under this
                                             username?
                                          ''',
                                          T.br(),
                                          '''
                                             After the removal you will be logged out
                                             and redirected to the Welcome page.
                                          '''
                                      ]
                                ],                                                
                                T.div(render=T.directive('form confirm')),
                                T.script(language='javascript')['document.forms[0].action[1].focus();'],
                                ]
                        ]
                    ]
    
    def form_confirm(self, ctx):
        f=formal.Form()
        f.addAction(self.confirm, name='confirm', label='Confirm')
        f.addAction(self.cancel, name='cancel', label='Cancel', validate=False)
        return f
    
    def confirm(self, ctx, form, data):
        def _cb(r):
            log.msg('Successfuly removed account %s' % self.user.username)
            return url.here.click('/'+guard.LOGOUT_AVATAR)
        def _eb(f):
            log.err('Error during removal of account %s' % self.user.username)
            return url.here.up()
            
        return self.user.deleteSingleUser(self.user.user_id).addCallbacks(_cb, _eb)
    
    def cancel(self, ctx, form, data):
        return url.here.up()
         
class UsersPage(base.AuthenticatedTwistPage):
        
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['User Management'],
                           T.h3['Registered users:'],
                           T.form(action=url.here.child('form_action'), method="post", class_='nevow-form', enctype='multipart/form-data')[
                               T.table(data=T.directive('users'), render=T.directive('sequence'))[
                                   T.tr(pattern='header', render=T.directive('header')),
                                   T.tr(pattern='item', class_='rowA', render=T.directive('user_item')),
                                   T.tr(pattern='item', class_='rowB', render=T.directive('user_item')),
                                ],
                                T.div(render=T.directive('actions'), class_='actions'),           
                           ],
                           T.script(language='javascript')['document.forms[0].action[0].focus();'],
                       ]
#                   ]
               ]

    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='5%')[''],
                       T.th(width='15%')['Username'], 
                       T.th(width='15%')['First Name'], 
                       T.th(width='15%')['Last Name'],
                       T.th(width='30%')['Email'],
                       T.th(width='10%')['Role'],
                       T.th(width='10%')['Enabled']
                       ]
         
    def data_users(self, ctx, data):
        return self.user.getAllUsers()
    
    
    def render_user_item(self, ctx, user):
        if user['user_id']==self.user.user_id:
            style='active'
        else:
            style='normal'
        return ctx.tag[T.td(_class=style)[T.input(type='checkbox', name='id_%s' % user['user_id'], value='True')],
                       T.td(_class=style)[user['username']],
                       T.td(_class=style)[user['first_name']],
                       T.td(_class=style)[user['last_name']],
                       T.td(_class=style)[user['email']],
                       T.td(_class=style)[user['role']],
                       T.td(_class=style)[user['enabled']],
                       ]

    def render_actions(self, ctx, data):
        return ctx.tag[T.input(type='submit', name='action', value='Add'),
                       T.input(type='submit', name='action', value='Edit',), 
                       T.input(type='submit', name='action', value='Purge'),
                ]
            
    def child_form_action(self, ctx):

        req=inevow.IRequest(ctx)
        try:
            action=req.args['action'][0]
        except KeyError:
            action=None
        if action=='Add':
            return url.here.sibling('add').clear()
        else:
            selection=[int(key.split('_')[1]) for key in req.args.keys() if (key.startswith('id') and req.args[key][0]=='True')]
            if selection:
                if action=='Edit':
                    u=url.here.sibling('edit').clear()
                    for id in selection:
                        u=u.add('user_id', id)
                    return u
                elif action=='Purge':
                    u=url.here.sibling('purge').clear()
                    for id in selection:
                        u=u.add('user_id', id)
                    return u
        return url.here.up()
    
    def child_purge(self, ctx):
        return PurgeUsersPage(self.user)

    def child_edit(self, ctx):
        return EditUserPage(self.user)

    def child_add(self, ctx):
        return AddUserPage(self.user)


class PurgeUsersPage(base.AuthenticatedTwistPage):

    def __init__(self, user):
        super(PurgeUsersPage, self).__init__(user)
        self.id_list=[]
       
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['User Management'],
                           T.h3['Deleting users:'],
                           T.invisible(data=T.directive('users'), render=T.directive('if'))[
                               T.div(pattern='True')[
                                   T.blockquote['''Warning: About to purge the following list of users. 
                                                   This would also remove all referenced jobs by the users both 
                                                   in the active and in the archived job table!'''],
                                   T.table(render=T.directive('sequence'))[
                                       T.tr(pattern='header', render=T.directive('header')),
                                       T.tr(pattern='item', class_='rowA', render=T.directive('user_item')),
                                       T.tr(pattern='item', class_='rowB', render=T.directive('user_item')),
                                   ],
                                   T.span(render=T.directive('form confirm')),
                                   T.script(language='javascript')['document.forms[0].cancel.focus();'],
                               ],
                               T.div(pattern='False')[
                                   T.p['''You have insufficient rights for the operation or 
                                          you are trying to modify a non-existing item.''',
                                       T.span(render=T.directive('back_link'))
                                   ]
                               ]
                           ]
                       ]
#                   ]
               ]
        
    def render_header(self, ctx, data):
        return ctx.tag[T.th(width='20%')['Username'], 
                       T.th(width='15%')['First Name'], 
                       T.th(width='15%')['Last Name'],
                       T.th(width='30%')['Email'],
                       T.th(width='10%')['Role'],
                       T.th(width='10%')['Enabled']
                       ]
        
    def data_users(self, ctx, data):
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['user_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                return []

        try:
            self.id_list.remove(self.user.user_id) # make sure we are not removing the current account
        except ValueError:
            pass
        
        if self.id_list:
            return self.user.getListUsers(self.id_list)
        else:    
            return []
    
    def render_user_item(self, ctx, user):
        return ctx.tag[T.td[user['username']],
                       T.td[user['first_name']],
                       T.td[user['last_name']],
                       T.td[user['email']],
                       T.td[user['role']],
                       T.td[user['enabled']],
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
                return self.user.deleteListUsers(id_list).addCallback(_cb)
            else:
                return url.here.up()
        except KeyError:
            return url.here.up()
    
    def cancel(self, ctx, form, data):
        return url.here.up()
    
    
class AddUserPage(base.AuthenticatedTwistPage):
       
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['User Management'],
                           T.h3['Adding new user:'],
                               T.div(render=T.directive('form addUser')),
                               T.script(language='javascript')['document.forms[0].first_name.focus();'],
                       ]
#                   ]
               ]
        
    def form_addUser(self, ctx):
        f=formal.Form()
        f.addField('first_name', formal.String(required=True, validators=[formal.LengthValidator(max=20)]), label='First Name')
        f.addField('last_name', formal.String(required=True, validators=[formal.LengthValidator(max=20)]), label='Last Name')
        f.addField('email', formal.String(required=True, validators=[formal.LengthValidator(max=50),
                                                                     formal.PatternValidator(r'.+@[a-zA-Z\.\-]+')]), 
                                             label='Email')
        f.addField('username', formal.String(required=True,validators=[formal.LengthValidator(min=6),
                                                                          formal.PatternValidator(r'^[a-zA-Z_\-0-9]*$'),
                                                                          UsernameValidator(ctx),]),
                                                label='Choose a username')
        f.addField('passwd', formal.String(required=True, validators=[formal.LengthValidator(min=8)]),
                                                                         formal.widgetFactory(formal.CheckedPassword), 
                                                label='Choose a password')
        f.addField('role', formal.String(required=True), formal.widgetFactory(formal.SelectChoice, 
                                                                              options=[('admin', 'Administrator'),
                                                                                       ('user', 'User'),
                                                                                       ('requested','Approval pending')]),
                                                 label='Role')
        
        f.addField('enabled', formal.Boolean(required=True), formal.widgetFactory(formal.Checkbox), label='Enabled')
        
        f.data={'role':'user', 'enabled':True}
        f.addAction(self.addSingleUser, label='Add')
        f.addAction(self.cancel, name='cancel', label='Cancel', validate=False)
        return f

    def addSingleUser(self, ctx, form, data):
        
        if data['enabled'] and data['role']=='requested':
            raise formal.FieldValidationError(u'Account can not be enabled while approval pending status not cleared.', fieldName='enabled')
            
        def _cb(result):
                return url.here.up()
        def _eb(f):
            log.err('Error during adding a new account.')
            return url.here.up()        
        return self.user.addSingleUser(data).addCallbacks(_cb, _eb)
    
    def cancel(self, ctx, form, data):
        return url.here.up()


class EditUserPage(base.AuthenticatedTwistPage):
    
    
    def __init__(self, user):
        super(EditUserPage, self).__init__(user)
        self.id_list=[]
    
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['User Management'],
                           T.h3['Editing user info:'],
                           T.invisible(data=T.directive('users'), render=T.directive('if'))[
                               T.div(pattern='True', render=T.directive('form editUser')),
                               T.div(pattern='False')[
                                   T.p['''You have insufficient rights for the operation or 
                                          you are trying to modify a non-existing item.''',
                                       T.span(render=T.directive('back_link'))
                                   ]
                               ],
                               T.script(language='javascript')['document.forms[0].first_name.focus();'],
                           ]
                       ]
#                   ]
               ]
    
    def data_users(self, ctx, data):
        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['user_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                return []
        if self.id_list:
            return self.user.getListUsers(self.id_list)
        else:    
            return []
      
    def form_editUser(self, ctx):
        f=formal.Form()
        f.addField('user_id', formal.Integer(), widgetFactory=formal.Hidden)

        f.addField('first_name', formal.String(required=True, validators=[formal.LengthValidator(max=20)]), label='First Name')
        f.addField('last_name', formal.String(required=True, validators=[formal.LengthValidator(max=20)]), label='Last Name')
        f.addField('email', formal.String(immutable=True), label='Email')
        f.addField('username', formal.String(immutable=True), label='Username')
        f.addField('passwd', formal.String(required=False, validators=[formal.LengthValidator(min=8)]),
                                                                         formal.widgetFactory(formal.CheckedPassword), 
                                                label='New Password', description='Leave blank to retain the old password')
        f.addField('role', formal.String(required=True), formal.widgetFactory(formal.SelectChoice, 
                                                                              options=[('admin', 'Administrator'),
                                                                                       ('user', 'User'),
                                                                                       ('requested','Approval pending')]),
                                                 label='Role')
        
        f.addField('enabled', formal.Boolean(required=True), formal.widgetFactory(formal.Checkbox), label='Enabled')
        

        f.addAction(self.updateSingleUser, label='Update')
        f.addAction(self.cancel, name='cancel', label='Cancel', validate=False)
        
        
        def _cb(data, f):
            if data and data[0]['user_id']==self.id_list[0]:
                f.data=data[0]
            else:
                f.data={}
            return f
        def _eb(f):
            log.err('%s:%s' % (f.getErrorMessage, f.getTraceback()))
            f.data={}            
            return f

        if not self.id_list:
            try:
                req=inevow.IRequest(ctx)
                id_list_string=req.args['user_id']
                self.id_list=[int(id) for id in id_list_string]
            except (KeyError, ValueError):
                pass
        if self.id_list:
            d=self.user.getSingleUser(self.id_list[0])
            d.addCallback(_cb, f)
            d.addErrback(_eb)
            return d
        else:
            return f
        
    def updateSingleUser(self, ctx, form, data):
        try:
            user_id=data['user_id']
        except KeyError:
            raise formal.FormError('Insufficient permissions or editing a non-existing user!')
       
        self.id_list=[user_id]
       
        if data['enabled'] and data['role']=='requested':
            raise formal.FieldValidationError(u'Account can not be enabled while approval pending status not cleared.', fieldName='enabled')

        def _cb(result):
                return url.here.up()
        def _eb(f):
            log.err('%s:%s' % (f.getErrorMessage, f.getTraceback()))
            return url.here.up()
                
        return self.user.updateSingleUser(user_id, data).addCallbacks(_cb, _eb)
    
    def cancel(self, ctx, form, data):
        return url.here.up()
