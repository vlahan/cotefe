# this script is a test for the pytz module
# pytz creates datatime objects which are aware of time zones and dst
# calculates automatically day light saving time!

from datetime import datetime, tzinfo
import pytz

# UTC time zone
utc = pytz.utc

# Europe/Berlin time zone
berlin = pytz.timezone('Europe/Berlin')

# string format
FMT = '%Y-%m-%dT%H:%M:%S'

# creates a datetime object
dt = datetime.now()

# adds information about time zone Europe/Berlin
print 'DATETIME REPRESANTATION IN %s' % (berlin)
dt_berlin = berlin.localize(dt)
print dt_berlin.strftime(FMT)

# translates into time zone UTC
print 'DATETIME REPRESANTATION IN %s' % (utc)
dt_utc = dt_berlin.astimezone(utc)
print dt_utc.strftime(FMT)

# takes a datetime string
dt_str = '2011-09-01T12:00:00'

# creates a datetime object out of it
dt = datetime.strptime(dt_str, FMT)

# adds information about time zone UTC
print 'DATETIME REPRESANTATION IN %s' % (utc)
dt_utc= utc.localize(dt)
print dt_utc.strftime(FMT)

# translates into time zone Europe/Berlin
print 'DATETIME REPRESANTATION IN %s' % (berlin)
dt_berlin = dt_utc.astimezone(berlin)
print dt_berlin.strftime(FMT)
