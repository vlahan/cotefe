from datetime import datetime, tzinfo
import pytz

# UTC
utc = pytz.utc

# Europe/Berlin
berlin = pytz.timezone('Europe/Berlin')

FMT = '%Y-%m-%dT%H:%M:%S'

dt = datetime.now()





print 'DATETIME REPRESANTATION IN %s' % (berlin)
dt_berlin = berlin.localize(dt)
print dt_berlin.strftime(FMT)

print 'DATETIME REPRESANTATION IN %s' % (utc)
dt_utc = dt_berlin.astimezone(utc)
print dt_utc.strftime(FMT)

dt_str = '2011-09-01T12:00:00'

dt = datetime.strptime(dt_str, FMT)

print 'DATETIME REPRESANTATION IN %s' % (utc)
dt_utc= utc.localize(dt)
print dt_utc.strftime(FMT)

print 'DATETIME REPRESANTATION IN %s' % (berlin)
dt_berlin = dt_utc.astimezone(berlin)
print dt_berlin.strftime(FMT)
