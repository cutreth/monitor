from django.http import HttpResponse

import monitor.do as do

import datetime
import pytz
from postmark import PMMail

def floatFromPost(request, field):
    '''Returns float() or float(0) for a given POST parameter'''
    value = float(0)
    try:
        data = request.POST.get(field)
        if bool(data):
            value = float(data)
    finally:
        return value

def stringFromPost(request, field):
    '''Returns str() or str('') for a given POST parameter'''
    value = str('')
    try:
        data = request.POST.get(field)
        if bool(data) and str(data) != str(0):
            value = str(data)
    finally:
        return value

def intFromPost(request, field):
    '''Returns int() or int(0) for a given POST parameter'''
    value = int(0)
    try:
        data = request.POST.get(field)
        if bool(data):
            value = int(data)
    finally:
        return value

def allDataBlank(sensor_data):
    '''True if all data is greater than zero'''
    flag = True #Assume all data is blank
    for data in sensor_data:
        if data > 0:
            flag = False #Disable flag if data exists
    return flag

def allDataPositive(sensor_data):
    '''False if any data is less than zero'''
    flag = True #Assume all data is positive
    for data in sensor_data:
        if data < 0:
            flag = False #Disable flag if values are negative
    return flag

def getTempUnit(request):
    '''Returns 'F' (default) or 'C' for a given POST parameter'''
    temp_unit = 'F'
    try:
        data = stringFromPost(request, 'temp_unit')
        if bool(data):
            data = data[0].capitalize() #Take first letter and capitalize
        if temp_unit == 'C':
            temp_unit = data #Only update temp_unit if data == 'C'
    finally:
        return temp_unit

def getInstantOverride(request):
    '''Returns a datetime from an int() for a given POST parameter'''
    try:
        instant_override = intFromPost(request, 'instant_override')
        if instant_override > 0:
            instant_override = instant_override
            utc = pytz.utc
            instant_override = datetime.datetime.fromtimestamp(instant_override,tz=utc)
        else:
            instant_override = int(0)
    finally:
        return instant_override

def MaxMinCheck(base, deviation, value, category):
    '''Returns an error string if the input value exceeds the calculated bounds'''
    error = None
    if bool(base) and bool(deviation):
        upper = base + deviation
        lower = base - deviation
        if not (lower < value < upper):
            error = 'Sensor value of ' + str(round(value,2)) + ' outside range of {'
            error = error + str(lower) + ', ' + str(upper) + '} '
    return error

def SetErrorInfo(error_flag, error_details, error):
    '''Sets error_flag/error_details if an error is passed in'''
    if bool(error):
        error_flag = True
        error_details = error_details + error
    return [error_flag, error_details]

def MissingErrorCheck(read_missing, read_last_instant, time_delta):
    right_now = do.nowInUtc()
    read_expected = True #Assume need a reading
    if read_missing > 0:
        if bool(read_last_instant):
            if not isTimeBefore(read_last_instant, right_now, time_delta):
                read_expected = False
    else:
        read_expected = False
    return read_expected

def BoundsErrorCheck(active_config, read):
    '''Check for errors, update Reading record, output True if errors found'''
    error_flag = False
    error_details = str('')
    beer = do.getActiveBeer()
    category = 'Bounds'

    #Think about breaking these into arrays to simply adding more sensors
    error_cat = 'temp_amb'
    temp_amb_base = active_config.temp_amb_base
    temp_amb_dev = active_config.temp_amb_dev
    temp_amb = read.get_temp_amb()
    error = MaxMinCheck(temp_amb_base, temp_amb_dev, temp_amb, error_cat)
    [error_flag, error_details] = SetErrorInfo(error_flag, error_details, error)
    if bool(error):
        do.createEvent(beer, read, category, error_cat, error)
        error = None

    error_cat = 'temp_beer'
    temp_beer_base = active_config.temp_beer_base
    temp_beer_dev = active_config.temp_beer_dev
    temp_beer = read.get_temp_beer()
    error = MaxMinCheck(temp_beer_base, temp_beer_dev, temp_beer, error_cat)
    [error_flag, error_details] = SetErrorInfo(error_flag, error_details, error)
    if bool(error):
        do.createEvent(beer, read, category, error_cat, error)
        error = None

    read.error_flag = error_flag
    read.error_details = error_details
    return error_flag

def BuildErrorEmail(active_config, read, error_details):
    '''Construct an email; read.error_details then error_details (string)'''
    email_api_key = active_config.email_api_key
    email_sender = active_config.email_sender
    email_to = active_config.email_to
    email_subject = active_config.email_subject

    if bool(read):
        email_text_body = read.error_details
    elif bool(error_details):
        email_text_body = error_details
    else:
        email_text_body = 'Unspecified error'

    message = PMMail(api_key=email_api_key, sender=email_sender,
                     to=email_to, subject=email_subject,
                     text_body=email_text_body)
    return message

def isTimeBefore(reference, current, delta):
    '''Returns true if reference is before current minus delta
    (5AM, 7AM, 1 hour) -> True; (5AM, 7AM, 3 hours) -> False'''
    return (reference <= current - delta)

def SendErrorEmail(active_config, message):
    send_email = active_config.email_enable
    email_timeout = active_config.email_timeout
    email_last_instant = active_config.email_last_instant
    right_now = do.nowInUtc()
    time_delta = datetime.timedelta(minutes=email_timeout)

    if send_email and bool(message): #Email if no last instant or if cooldown is over
        if not bool(email_last_instant) or isTimeBefore(email_last_instant, right_now, time_delta):
            active_config.email_last_instant = right_now
            active_config.save()
            message.send()

def createHttpResp(read, value):
    '''Output an HttpResponse with all key variables'''
    response = HttpResponse(value)
    if bool(read):
        response['light_amb'] = read.light_amb
        response['pres_beer'] = read.pres_beer
        response['temp_beer'] = read.temp_beer
        response['temp_amb'] = read.temp_amb
        response['temp_unit'] = read.temp_unit
        response['instant_override'] = read.instant_override
        response['instant'] = read.instant
        response['instant_actual'] = read.instant_actual_iso
        response['error_flag'] = read.error_flag
        response['error_details'] = read.error_details
    return response
