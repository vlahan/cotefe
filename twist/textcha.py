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
import random
from twisted.python import log, util as tutil

import ConfigParser
config=ConfigParser.SafeConfigParser()

config.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

class TwistTextCha(object):
    '''Basic spam protection using Text CAPTCHAs inspired from MoinMoin'''
    
    def __init__(self):
        try:
            self.enabled=config.getboolean('web', 'enable_captchas')
        except (ConfigParser.ParsingError, ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            log.err('TextCha: Error parsing config file for enable_captchas option')
            self.enabled=False

        self.textchas={}
        if self.enabled:
            try:
                qalist=[qa for (t, qa) in config.items('captchas')]
                self.textchas=dict([qa.split(':') for qa in qalist])
                self.drawQA()
            except (ConfigParser.NoSectionError, ValueError, IndexError):
                log.err('TextCha: Error parsing config file for captchas')
                self.enabled=False
                               
            
    def drawQA(self):
        if self.enabled:
            if self.textchas:
                try:
                    self.question=random.choice(self.textchas.keys())
                    self.answer_re = re.compile(self.textchas[self.question], re.U|re.I)
                except (re.error):
                    log.err('Error drawing QA text captcha combination.')
                    self.drawQA()
            else:
                self.question='Unsolvable question (text captcha error)?'
                self.answer_re=re.compile(ur'[^.]*')
                log.err('TextCha: Empty QA captcha list. All answers will fail')
        
    def validate(self, answer):
        if self.enabled:
            if answer and self.answer_re.match(answer.strip()) is not None:
                self.drawQA()
                return True
            else:
                return False
        else:
            return True
