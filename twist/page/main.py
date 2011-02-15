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

from nevow import tags as T

import base
import user
import job
import supernodes

class WelcomePage(base.TwistPage):
    
    addSlash=True
        
    def render_corefrag(self, ctx, data):
        return ctx.tag[
 #                  T.div(id='primaryContentContainer')[
                       T.div(id='primaryContent')[    
                           T.h2['Welcome to the TWIST Web Interface'],
                           T.p['Hi. Please select an action from the menu above...'],
                           T.p['More information about TWIST can be found at the ',
                               T.a(href='http://www.twist.tu-berlin.de')['TWIST Community Wiki'],
                               ' site, including a ',
                               T.a(href='http://www.twist.tu-berlin.de' \
                                        '/wiki/TWIST/Instances/TKN' \
                                        '/Documentation/Tutorial')['Tutorial'],
                               ' on using this web interface.'
                           ],
                           T.blockquote['Make sure that cookies are enabled in your browser!']
                       ]
#                    ]
               ]

    def child_login(self, ctx):
        return user.LogInPage(self.user)
    
    def child_request_account(self, ctx):
        return user.RequestAccountPage(self.user)


class LoggedInPage(base.AuthenticatedTwistPage):
    
    addSlash=True
    
    def child_my_info(self, ctx):
        return user.MyInfoPage(self.user)
    
    def child_users(self, ctx):
        if self.user.role=='admin':
            return user.UsersPage(self.user)

    def child_supernodes(self, ctx):
            return supernodes.SupernodeManagementPage(self.user)
    
    def child_jobs(self, ctx):
        return job.JobsPage(self.user)
