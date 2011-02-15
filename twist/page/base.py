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
import datetime
import re

from twisted.python import log, failure, util as tutil
from nevow import inevow, loaders, rend, static, flat, tags as T, url, guard
import formal

import ConfigParser
config=ConfigParser.SafeConfigParser()

config.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

web_announcement = config.get('web','announcement')

def flattenDateTime(date, ctx):
    today = datetime.datetime.today()
    if today.date() == date.date():
        fmt = "Today <br> %H:%M"
    else:
        fmt = "%d %b %Y <br> %H:%M"
    return date.strftime(fmt)

flat.registerFlattener(flattenDateTime, datetime.datetime)

pl_map={1: 'eyesIFX v2.1', 2: 'eyesIFX v2.0', 3: 'TelosA', 4: 'TelosB', 5: 'Tmote'}

job_re=re.compile(r'^TwistDBException: (?P<msg>.*)\(job_id: (?P<job_id>\d+)\)')

class TwistPage(formal.ResourceMixin, rend.Page):

    docFactory = loaders.stan(
                    T.invisible[
                        T.xml('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'),
                        T.html[
                            T.head[
                                T.xml('<meta http-equiv="content-type" content="text/html; charset=utf-8" />'),
                                T.title(data=T.directive('title'), render=T.directive('string')),
                                T.link(href='/css/twist.css', rel='stylesheet', type='text/css'),
                            ],
                            T.body[
                                T.div(id='outer')[
                                    T.div(id='header')[
                                        T.h1['Tkn Wireless Indoor Sensor network Testbed'],
                                        T.h2(data=T.directive('navigation'), render=T.directive('navigation')),
                                    ],
                                    T.div(id='announcement', render=T.directive('announcement')),
                                    T.div(id='menu')[
                                        T.ul(data=T.directive('menu'), render=T.directive('sequence'))[
                                            T.li(pattern='item', render=T.directive('menu_item')),
                                            T.li(pattern='footer', render=T.directive('logout'))
                                        ]
                                    ],
                                    T.div(id='content', render=T.directive('corefrag')),
                                    T.div(_class='clear'),
                                    T.div(id='footer')[
                                        T.p[T.xml('Copyright &copy Telecommunication Networks Group. Site designed using '),
                                            T.a(href='http://www.freecsstemplates.org')['free CSS Templates.'],
                                        ]
                                    ]
                                ]
                            ]
                        ]
        ])
    
    
    child_images=static.File('static/images')
    child_css= static.File('static/css')


    def __init__(self, user):
        super(TwistPage, self).__init__()
        self.user=user
        print 'Creating new resource %s for user %s' % (self.__class__.__name__, self.user.username)

    def locateChild(self, ctx, segments):
        ctx.remember(self, inevow.ICanHandleException)
        ctx.remember(self, inevow.ICanHandleNotFound)
        return super(TwistPage, self).locateChild(ctx, segments)

    def willHandle_notFound(self, request):
        return True

    def renderHTTP_notFound(self, ctx):    
        return The404Page(self.user).renderHTTP(ctx)

    def willHandle_exception(self, request, failure):
        return True

    def renderHTTP_exception(self, ctx, f):
        if isinstance(f, failure.Failure):
            msg=f.getErrorMessage().strip()
        else:
            msg=str(f)
        log.err('Anonymous exception: %s' % msg)
        req = inevow.IRequest(ctx)
        req.setResponseCode(500)
        res = The500Page(self.user).renderHTTP(ctx)
        req.finishRequest(False)
        return res

    def render_corefrag(self, ctx, data):
        return ''

    def data_title(self, ctx, data):
        return 'TWIST Web Interface'

    def data_navigation(self, ctx, data):
        return [datetime.datetime.today().strftime('%d %b %Y (%H:%M)')]
    
    def render_navigation(self, ctx, data):
        return ctx.tag[T.p[[(item, T.br()) for item in data]]]
    
    def render_announcement(self, ctx, data):
        return ctx.tag[T.blockquote[web_announcement]]
        
    def data_menu(self, ctx, data):
        return [('/login', 'Login'), ('/request_account', 'New account')]

    def render_menu_item (self, ctx, data):
        url, text = data
        return ctx.tag[T.a(href=url)[text]]

    def render_logout(self, ctx, data):
        return ''
 
    def render_if(self, ctx, data):
        q = inevow.IQ(ctx)
        true_pattern = q.onePattern('True')
        false_pattern = q.onePattern('False')
        
        if data:
            return true_pattern or ctx.tag().clear()
        else:
            return false_pattern or ctx.tag().clear()

    def render_back_link(self, ctx, data):
        req=inevow.IRequest(ctx)
        referer = req.getHeader('referer')
        if referer:
            return T.p['Back to the ', T.a(href=referer)['previous page...']]
        else:
            return T.p['Back to the ', T.a(href=url.root.clear())['start page...']]

  
    def render_lastLink(self, ctx, data):
        req = inevow.IRequest(ctx)
        referer=req.getHeader('referer')
        if self.user.role in ('user', 'admin') and referer:
            return T.p[T.a(href=referer)['This link'],
                       ' will return you to the last page you were on.']
        elif self.user.role=='anon':
            u = url.root.child('login').clear().add('urlTo', req.uri)
            return ctx.tag[
                       T.p['You are signed off or your session has expired!'],
                       T.p['Please ', T.a(href=u)[T.b['sign in']],  
                           ' and you will be redirected to the requested resource.']
                    ]
        else:
            return T.p['You seem to be hopelessly lost.']

        
setattr(TwistPage, 'child_js', formal.formsJS)
setattr(TwistPage, 'child_formal.css', formal.defaultCSS)

class ErrorPage(TwistPage):

    docFactory = loaders.stan(
                    T.invisible[
                        T.xml('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'),
                        T.html[
                            T.head[
                                T.xml('<meta http-equiv="content-type" content="text/html; charset=utf-8" />'),
                                T.title(data=T.directive('title'), render=T.directive('string')),
                                T.link(href='/css/twist.css', rel='stylesheet', type='text/css'),
                            ],
                            T.body[
                                    T.div(id='content', render=T.directive('corefrag')),
                                    T.div(_class='clear'),
                                    T.div(id='footer')[
                                        T.p[T.xml('Copyright &copy Telecommunication Networks Group. Site designed using '),
                                            T.a(href='http://www.freecsstemplates.org')['free CSS Templates.'],
                                        ]
                                    ]
                                ]
                            ]
        ])
    

    
    def render_corefrag (self, ctx, data):
        return ctx.tag[
                        T.div(id='primarycontent')[
                            T.h2['TWIST web interface error!'],
                            T.div(id='content')[
                                      T.blockquote[
                                          T.i['Error:'], T.br(),
                                          T.span(render=T.directive('error')),
                                          T.p(render=T.directive('lastLink'))
                                      ],
                                      T.blockquote['Make sure cookies are enabled in your browser!']
                                ]
                            ]
                    ]
                    
class The500Page(ErrorPage):
#    implements(inevow.ICanHandleException)

    def render_error(self, ctx, data):
        return T.p['Oops. Internal server error. We apologize for the inconvenience. Please try later!']
    
class The404Page(ErrorPage):
#    implements(inevow.ICanHandleNotFound)
    
    def render_error(self, ctx, data):
        return ctx.tag[
                   T.p['The resource you have requested is missing!']
               ]

class AuthenticatedTwistPage(TwistPage):
    
    def locateChild(self, ctx, segments):
        ctx.remember(self, inevow.ICanHandleNotFound)
        ctx.remember(self, inevow.ICanHandleException)
        return super(AuthenticatedTwistPage, self).locateChild(ctx, segments)
    
    def willHandle_exception(self, request, failure):
        return True

    def renderHTTP_exception(self, ctx, f):
        print f
        if isinstance(f, failure.Failure):
            msg=f.getErrorMessage().strip()
        else:
            msg=str(f)
        log.err('Authenticated exception: %s' % msg)
        req = inevow.IRequest(ctx)
        req.setResponseCode(500)
        res = TheAuthenticated500Page(self.user).renderHTTP(ctx)
        req.finishRequest(False)
        return res

    def willHandle_notFound(self, request):
        return True

    def renderHTTP_notFound(self, ctx):
        req = inevow.IRequest(ctx)
        req.setResponseCode(404)
        res = TheAuthenticated404Page(self.user).renderHTTP(ctx)
        req.finishRequest(True)
        return res
    
    def beforeRender (self, ctx):
        ctx.fillSlots('username', self.user.username)
        ctx.fillSlots('first_name', self.user.first_name)
        ctx.fillSlots('last_name', self.user.last_name)

    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Welcome to TWIST, ',
                                T.slot(name='first_name'), ' ',
                                T.slot(name='last_name'), '!'],
                           T.b['Please select an action from the top menu!']
                       ]
#                   ]
               ]
    
    def data_title(self, ctx, data):
        return 'TWIST Web Interface %s: %s' % (self.user.username, self.__class__.__name__.replace ("_", " "))

    def data_navigation(self, ctx, data):
        return ['%s: %s' % (self.user.username, self.__class__.__name__[:-4]),
                datetime.datetime.today().strftime('%d %b %Y (%H:%M)')]
    
    def data_menu(self, ctx, data):
        menu=[]
        menu.append(('/my_info', 'My Info'))            
        if self.user.role=='admin':
            menu.append(('/users', 'Users'))
        menu.append(('/jobs', 'Jobs'))
        menu.append(('/supernodes', 'Supernodes'))
        return menu

    def render_logout(self, ctx, data):
        return ctx.tag[T.a(href='/'+guard.LOGOUT_AVATAR)['Logout']]

class AuthenticatedErrorPage(ErrorPage):
    
    def render_corefrag (self, ctx, data):
        return ctx.tag[
#                   T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['TWIST web interface error!'],
                           T.div[
                               T.blockquote[
                                   T.i['Error:'], T.br(),
                                   T.span(render=T.directive('error'))
                               ]
                           ],
                           T.div(render=T.directive('back_link')),
                           T.blockquote['Make sure that cookies are enabled in your browser!']
                       ]
#                   ]
               ]
 

class TheAuthenticated500Page(AuthenticatedErrorPage):

    def render_error(self, ctx, data):
        return T.p['Oops. Internal server error. We apologize for the inconvenience. Please try later!']
    
class TheAuthenticated404Page(AuthenticatedErrorPage):
    
    def render_error(self, ctx, data):
        return T.p['The resource you have requested is missing!']
