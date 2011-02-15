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
# Based on the cal tag from Nevow

import calendar
import datetime
import colorsys

from nevow import tags as t, url, itaglibrary, rend, static

class CalendarComponent(object):
    current_date = None
    def days(self, year, month, jobs):
        
        def duration(t1, t2, t3, t4):
            if t1>t4 or t3>t2:
                return datetime.timedelta(0)
            else:
                l=[t1, t2, t3, t4]
                l.sort()
                return l[2]-l[1]
        
        def dayAndLoad(day, jobs):
            if day:
                t1=datetime.datetime(year, month, day)
                t2=t1+datetime.timedelta(days=1)
                load={}
                for job in jobs:
                    t3=job['time_begin']
                    t4=job['time_end']
                    d=duration(t1, t2, t3, t4)
                    h=int(round(d.days*24.0+d.seconds/3600.0))
                    for res in job['resources']:
                        load[res]=load.setdefault(res, 0)+h
                return t1, load
            else:
                return None, {}
                    
        
        def _(ctx, data):
            return [[dayAndLoad(day, jobs)
                     for day in row]
                         for row in calendar.monthcalendar(year, month)]
        return _

    def render_calendarDay(self, ctx, data):
        
        if data is not None:
            date, load = data
        if date is None:
            return ctx.tag['']
        
        eyes_load=max(load.get(1,0), load.get(2,0))/24.0
        telos_load=max(load.get(3,0),load.get(4,0),load.get(5,0))/24.0
        
        if eyes_load==0 and telos_load==0:
            bg_col='#FFFFFF'
        else:
            eyes_hsv=list(colorsys.rgb_to_hsv(1.0, 0, 0))
            telos_hsv=list(colorsys.rgb_to_hsv(0, 0, 1.0))
            
            eyes_hsv[1]=eyes_load
            telos_hsv[1]=telos_load
            
            bg_hsv=[0,0,0]

            bg_hsv[0]=(eyes_hsv[0]*eyes_hsv[1]+telos_hsv[0]*telos_hsv[1])/(telos_hsv[1]+eyes_hsv[1])
            
            bg_hsv[1]=0.1+(eyes_hsv[1]+telos_hsv[1])/2.0

            if bg_hsv[1]>1.0:
                bg_hsv[1]=1.0
                
            bg_hsv[2]=max(eyes_hsv[2],telos_hsv[2])
            
                       
            bg_rgb=colorsys.hsv_to_rgb(*bg_hsv)
            
            bg_col='#%02X%02X%02X' % tuple([int(color*255.0) for color in bg_rgb])
        
        if self.current_date.day == date.day and \
           self.current_date.month == date.month and \
           self.current_date.year == date.year:
            return ctx.tag(style='background-color:%s; font-weight: bold;' % bg_col)[date.day]
        else:
            return ctx.tag(style='background-color:%s;' % bg_col)[date.day]

    def render_today(self, ctx, data):
        base = None
        strftime = '%b %d, %Y @ %H:%M %p'
        if base is None:
            u=url.URL.fromContext(ctx)
            u=u.remove('year')
            u=u.remove('month')
            u=u.add('year', self.current_date.year)
            u=u.add('month', self.current_date.month)
            return ctx.tag[
                       t.a(href=u)[self.current_date.strftime(strftime)]
                   ]
                                               
    def calendar(self, ctx, data):
        now = datetime.datetime.now()
        self.current_date = now
        month_delta = datetime.timedelta(31)
        strftime = '%b %d, %Y @ %H:%M %p'
        width =  2
        prev = None
        next = None
        base = None
        calendar_class = 'calendar'
        
        if data is not None:
            d, jobs = data
        else:
            d = now
            jobs=[]

        if prev is None or next is None:
            d=d.replace(day=4)
            p = d - month_delta
            n = d + month_delta
            if base is None:
                u = url.URL.fromContext(ctx)
                prev_url = u
                next_url = u
            else:
                prev_url = base
                next_url = base
         
            u=prev_url
            u=u.remove('year')
            u=u.add('year', str(p.year))
            u=u.remove('month')
            u=u.add('month', str(p.month))
            prev_url=u

            u=next_url
            u=u.remove('year')
            u=u.add('year', str(n.year))
            u=u.remove('month')
            u=u.add('month', str(n.month))
            next_url=u
        else:
            if isinstance(prev, (url.URL, url.URLOverlay)) and \
               isinstance(next, (url.URL, url.URLOverlay)):
                next_url = next
                prev_url = prev
                
        return t.table(class_=calendar_class)[
            t.thead[
              t.tr[
                t.th(colspan="7")[
                   t.a(href=prev_url)[t.xml("&larr;")],
                   t.xml(" "),
                   t.xml('-'.join([str(el) for el in (d.year, d.month)])),
                   t.xml(" "),
                   t.a(href=next_url)[t.xml("&rarr;")]
                ]
              ],
              [
                t.tr[[t.td[dayname] for dayname in calendar.weekheader(width).split()]]
              ]
            ],
            t.tbody[
              t.invisible(data=self.days(d.year, d.month, jobs), render=rend.sequence)[
                 t.tr(pattern='item', render=rend.sequence)[
                     t.td(pattern='item', render=self.render_calendarDay)
                 ]
              ]
            ],
            t.tfoot[
               t.tr[
                  t.td(colspan="7", render=self.render_today)
               ]
            ]
        ]


c = CalendarComponent()
cal = c.calendar
__all__ = ["cal", "CalendarComponent", "calendarCSS", "calendarCSSFile"]
