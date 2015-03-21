from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

import calendar, datetime

from datetime import timedelta
from postmark import PMMail
from monitor.models import Beer, Reading, Config

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
            instant_override = datetime.datetime.fromtimestamp(instant_override)
            instant_override = instant_override - timedelta(hours=1)
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
            error = '[' + str(value) + ':' + str(lower) + '-' + str(upper) + '] '
            error = str(category) + ' ' + error
    return error

def SetErrorInfo(error_flag, error_details, error):
    '''Sets error_flag/error_details if an error is passed in'''
    if bool(error):
        error_flag = True
        error_details = error_details + error
    return [error_flag, error_details]

def ErrorCheck(active_config, read):
    '''Check for errors, update Reading record, output True if errors found'''
    error_flag = False
    error_details = str('')

    temp_amb_base = active_config.temp_amb_base
    temp_amb_dev = active_config.temp_amb_dev
    temp_amb = read.get_temp_amb()
    error_cat = 'temp_amb'
    
    error = MaxMinCheck(temp_amb_base, temp_amb_dev, temp_amb, error_cat)
    [error_flag, error_details] = SetErrorInfo(error_flag, error_details, error)

    temp_beer_base = active_config.temp_beer_base
    temp_beer_dev = active_config.temp_beer_dev
    temp_beer = read.get_temp_beer()
    error_cat = 'temp_beer'
    
    error = MaxMinCheck(temp_beer_base, temp_beer_dev, temp_beer, error_cat)
    [error_flag, error_details] = SetErrorInfo(error_flag, error_details, error)
    
    #Think about breaking these into arrays to simply adding more sensors

    read.error_flag = error_flag
    read.error_details = error_details
    return read.error_flag

def BuildErrorEmail(active_config, read, error_details):
    email_api_key = active_config.email_api_key
    email_sender = active_config.email_sender
    email_to = active_config.email_to
    email_subject = active_config.email_subject

    if bool(read):
        email_text_body = read.error_details
    elif bool(error_details):
        email_text_body = error_details
    else:
        email_text_body = 'Unspecified Error'

    message = PMMail(api_key = email_api_key,
                     sender = email_sender,
                     to = email_to,
                     subject = email_subject,
                     text_body = email_text_body)
    return message

def isTimeBefore(reference, current, delta):
    '''Returns true if reference is before current minus delta
    (5AM, 7AM, 1 hour) -> True; (5AM, 7AM, 3 hours) -> False'''    
    return (reference <= current - delta)

def SendErrorEmail(active_config, message):
    send_email = active_config.email_enable
    email_timeout = active_config.email_timeout
    email_last_instant = active_config.email_last_instant
    right_now = datetime.datetime.now()
    time_delta = datetime.timedelta(minutes=email_timeout)
    
    if send_email and bool(message): #Email if no last instant or if cooldown is over
        if not bool(email_last_instant) or isTimeBefore(email_last_instant, right_now, time_delta):
            active_config.email_last_instant = right_now
            active_config.save()
            message.send()

def createHttpResp(read, value):
    response = HttpResponse(value)
    if bool(read):
        response['light_amb'] = read.light_amb
        response['pres_beer'] = read.pres_beer
        response['temp_beer'] = read.temp_beer
        response['temp_amb'] = read.temp_amb
        response['temp_unit'] = read.temp_unit
        response['instant_override'] = read.instant_override
        response['instant'] = read.instant
        response['instant_actual'] = read.instant_actual
        response['error_flag'] = read.error_flag
        response['error_details'] = read.error_details
    return response

def SetReadInstant(active_config):
    right_now = datetime.datetime.now()
    active_config.read_last_instant = right_now
    active_config.save()
    return

#C:\Python34\python -m pdb manage.py runserver
#Then press 'c'
#import pdb; pdb.set_trace()

@csrf_exempt
def api(request):

    key = stringFromPost(request, 'key')
    if (key == 'beer') or (key == 'test'):

        active_config = Config.objects.get(pk=1) #Get config 1
        active_beer = active_config.beer #Get active beer

        read = Reading(beer=active_beer) #Create reading record

        #Populate sensor data
        light_amb = floatFromPost(request, 'light_amb')
        pres_beer = floatFromPost(request, 'pres_beer')
        temp_beer = floatFromPost(request, 'temp_beer')
        temp_amb = floatFromPost(request, 'temp_amb')

        sensor_data = [light_amb, pres_beer, temp_amb, temp_beer]

        if not allDataBlank(sensor_data) and allDataPositive(sensor_data):

            #All data set for every read
            read.light_amb = light_amb
            read.pres_beer = pres_beer
            read.temp_beer = temp_beer
            read.temp_amb = temp_amb

            #Get and set temp_unit
            temp_unit = getTempUnit(request)
            read.temp_unit = temp_unit

            #Get and set instant_override if it exists
            instant_override = getInstantOverride(request) #0 = NULL
            if bool(instant_override):
                read.instant_override = instant_override
            #instant_override will either be 0 or a datetime object

            #Check for deviation errors
            error_flag = ErrorCheck(active_config, read)

            #And finally, save the record
            if key == 'beer':
                read.save()
                SetReadInstant(active_config)
                if error_flag: #Send error emails if necessary
                    message = BuildErrorEmail(active_config, read, None)
                    SendErrorEmail(active_config, message)
                status = "Success"
            else:
                status = "Test Success"
        else:
            status = "Data Failure"
    else:
        status = "Key Failure"
        read = None #Not otherwise set outside the for loop

    #Generate and send a response per status flag with 'read' object data
    response = createHttpResp(read, status)
    return response






def ConvertDateTime(obj):
    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        else:
            obj = obj + timedelta(hours=5)
    millis = int(
        calendar.timegm(obj.timetuple()) * 1000 +
        obj.microsecond / 1000
    )
    return millis


def chart(request, cur_beer=None):

    all_beers = Beer.objects.all()

    if cur_beer is None:
        active_config = Config.objects.get(pk=1)
        active_beer = active_config.beer
    else:
        active_beer = Beer.objects.get(pk=cur_beer)

    active_readings = Reading.objects.filter(beer=active_beer)

    #I should use instant_actual here; rework when we rewrite this code
    xdata = [ConvertDateTime(n.instant_actual) for n in active_readings]
    if not bool(xdata):
        xdata.append(ConvertDateTime(datetime.datetime.now()))

    #Update to only show y-data where non-zero values exist
    temp_amb_data = [n.get_temp_amb() for n in active_readings]
    temp_beer_data = [n.get_temp_beer() for n in active_readings]
    light_amb_data = [n.get_light_amb() for n in active_readings]
    pres_beer_data = [n.get_pres_beer() for n in active_readings]

    #Doesn't respect ordering via Reading.instant_actual()
    error_readings = Reading.objects.filter(beer=active_beer).filter(error_flag=True)

    y1data = temp_amb_data
    y2data = temp_beer_data
    y3data = light_amb_data
    y4data = pres_beer_data

    xdata.append(min(xdata)-1)
    y1data.append(float(0))
    y2data.append(float(0))
    y3data.append(float(0))
    y4data.append(float(100))

    xydata = zip(xdata, y1data, y2data, y3data, y4data)
    xydata = sorted(xydata)

    xdata = [n[0] for n in xydata]
    y1data = [n[1] for n in xydata]
    y2data = [n[2] for n in xydata]
    y3data = [n[3] for n in xydata]
    y4data = [n[4] for n in xydata]

    beer_name = active_beer
    beer_date = active_beer.brew_date

    tooltip_date = "%m/%d %H:%M"
    extra_serie1 = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "date_format": tooltip_date,
        #'color': '#a239c6',
    }
    extra_serie2 = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "date_format": tooltip_date,
        #'color': '#395ec6',
    }
    extra_serie3 = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "date_format": tooltip_date,
        #'color': '#395ec6',
    }
    extra_serie4 = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "date_format": tooltip_date,
        #'color': '#395ec6',
    }

    chartdata = {'x': xdata,
                 'name1': 'Amb Temp', 'y1': y1data, 'extra1': extra_serie1,
                 'name2': 'Beer Temp', 'y2': y2data, 'extra2': extra_serie2,
                 'name3': 'Amb Light', 'y3': y3data, 'extra3': extra_serie3,
                 'name4': 'Pres Beer', 'y4': y4data, 'extra4': extra_serie4}

    charttype = "lineChart"
    chartcontainer = 'chart_container'  # container name
    data = {
        'all_beers': all_beers,
        'error_readings': error_readings,
        'beer_name': beer_name,
        'beer_date': beer_date,
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': True,
            'x_axis_format': '%m/%d %H:%M',
            'tag_script_js': True,
            'jquery_on_ready': False,
            'chart_attr': {'color':['orange', 'blue', 'green', 'purple']},
        }
    }
    return render_to_response('chart.html', data)
    