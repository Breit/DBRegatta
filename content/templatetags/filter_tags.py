import math
#import base64
import hashlib
from django import template

register = template.Library()

'''
Definition of a filter usable in a template that gets a fraction
of a float-based timedeta.
The parameter 'arg' can be one of {min, sec, hnd}
    - 'min' gets the full minutes
    - 'sec' gets the full seconds (up to 59)
    - 'hnd' gets the hundredth of a second (up to 99)
    - 'hnd' gets the milliseconds (up to 999)
Returns empty string on any error.
'''
@register.filter
def splitTime(value, arg):
    if arg not in ['min', 'sec', 'hnd', 'msec']:
        return ''
    try:
        value = float(value)
        minutes = math.floor(value / 60.0)

        if arg == 'min':
            return '{:02d}'.format(math.floor(minutes))
        elif arg == 'sec':
            return '{:02d}'.format(math.floor(value - minutes * 60.0))
        elif arg == 'hnd':
            return '{:02d}'.format(math.floor(round(1e2 * (value - math.floor(value)))))
        elif arg == 'msec':
            return '{:02d}'.format(math.floor(round(1e3 * (value - math.floor(value)))))
    except:
        pass

    return ''

'''
Definition of a filter usable in a template that properly
formats a float-based timedeta.
Returns empty string on any error.
'''
@register.filter
def asTime(value):
    try:
        if value is None:
            return '00:00.00'

        value = float(value)
        minutes = math.floor(value / 60.0)
        seconds = math.floor(value - minutes * 60.0)
        hundredth = math.floor(round(1e2 * (value - math.floor(value))))

        return '{:02d}:{:02d}.{:02d}'.format(minutes, seconds, hundredth)
    except:
        pass

    return ''

'''
Simple multiply filter
'''
@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except:
        pass

    return ''

'''
Simple summation filter
'''
@register.filter
def sumUp(value):
    try:
        return sum(value)
    except:
        pass

    return ''

'''
String startswith() filter
'''
@register.filter
def startswith(value, arg):
    try:
        if value.startswith(arg):
            return value.replace(arg, '')
    except:
        pass

    return ''

'''
String to id filter
Generate UID from string to use string as ID in HTML templates.
'''
@register.filter
def uid(value):
    try:
        m = hashlib.md5()
        m.update(value.encode('utf-8'))
        return 'id_' + m.hexdigest()
    except:
        pass

    return ''