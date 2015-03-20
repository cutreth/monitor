from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

import calendar, datetime

from datetime import timedelta
from postmark import PMMail
from monitor.models import Beer, Reading, Config

def floatFromPost(request, field):
    value = float(0)
    try:
        data = request.POST.get(field)
        if bool(data):
            value = float(data)
    finally:
        return value

def stringFromPost(request, field):
    value = str('')
    try:
        data = request.POST.get(field)
        if bool(data) and str(data) != str(0):
            value = str(data)
    finally:
        return value

def intFromPost(request, field):
    value = int(0)
    try:
        data = request.POST.get(field)
        if bool(data):
            value = int(data)
    finally:
        return value

def allDataBlank(sensor_data):
    flag = True #Assume all data is blank
    for data in sensor_data:
        if data > 0:
            flag = False #Disable flag if data exists
    return flag

def allDataPositive(sensor_data):
    flag = True #Assume all data is positive
    for data in sensor_data:
        if data < 0:
            flag = False #Disable flag if values are negative
    return flag

def getTempUnit(request):
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
    try:
        instant_override = intFromPost(request, 'instant_override')
        if instant_override > 0:
            instant_override = datetime.datetime.fromtimestamp(instant_override)
            instant_override = instant_override - timedelta(hours=1)
    finally:
        return instant_override

def ErrorCheck(active_config, read):

    #Enhance to add support for temperature conversions
    temp_amb_base = active_config.temp_amb_base
    temp_amb_dev = active_config.temp_amb_dev

    temp_beer_base = active_config.temp_beer_base
    temp_beer_dev = active_config.temp_beer_dev

    if bool(temp_amb_base) and bool(temp_amb_dev):
        temp_amb_max = temp_amb_base + temp_amb_dev
        temp_amb_min = temp_amb_base - temp_amb_dev

        if not (temp_amb_min < read.temp_amb < temp_amb_max):
            read.error_flag = True
            read.error_details = read.error_details + 'temp_amb: [' + str(temp_amb_min) + ', ' + str(temp_amb_max) + ']'
            read.error_details = read.error_details + ' *[' + str(read.temp_amb) + '] '
        elif read.error_flag is None:
            read.error_flag = False

    if bool(temp_beer_base) and bool(temp_beer_dev):
        temp_beer_max = temp_beer_base + temp_beer_dev
        temp_beer_min = temp_beer_base - temp_beer_dev

        if not (temp_beer_min < read.temp_beer < temp_beer_max):
            read.error_flag = True
            read.error_details = read.error_details + 'temp_beer: [' + str(temp_beer_min) + ', ' + str(temp_beer_max) + ']'
            read.error_details = read.error_details + ' *[' + str(read.temp_beer) + '] '
        elif read.error_flag is None:
            read.error_flag = False

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

def SendErrorEmail(active_config, message):

    send_email = active_config.email_enable
    email_timeout = active_config.email_timeout
    email_last_instant = active_config.email_last_instant

    right_now = datetime.datetime.now()

    if not bool(email_last_instant): #If last_instant is null, send email
        active_config.email_last_instant = right_now
        active_config.save()
    elif email_last_instant <= right_now - datetime.timedelta(minutes=email_timeout):
        active_config.email_last_instant = right_now
        active_config.save()
    else:
        send_email = False

    if send_email and bool(message):
        message.send()

def createHttpResp(read, value):

    response = HttpResponse(value)
    if bool(read):
        response['light_amb'] = read.light_amb
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
        temp_beer = floatFromPost(request, 'temp_beer')
        temp_amb = floatFromPost(request, 'temp_amb')

        sensor_data = [light_amb, temp_amb, temp_beer]

        if not allDataBlank(sensor_data) and allDataPositive(sensor_data):

            #All data set for every read
            read.light_amb = light_amb
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
    xdata = [ConvertDateTime(n.func_instant_actual()) for n in active_readings]
    if not bool(xdata):
        xdata.append(ConvertDateTime(datetime.datetime.now()))

    #Update to only show y-data where non-zero values exist
    temp_amb_data = [n.get_temp_amb() for n in active_readings]
    temp_beer_data = [n.get_temp_beer() for n in active_readings]
    light_amb_data = [n.get_light_amb() for n in active_readings]

    #Doesn't respect ordering via Reading.instant_actual()
    error_readings = Reading.objects.filter(beer=active_beer).filter(error_flag=True)

    y1data = temp_amb_data
    y2data = temp_beer_data
    y3data = light_amb_data

    xdata.append(min(xdata)-1)
    y1data.append(float(90))
    y2data.append(float(50))
    y3data.append(float(0))

    xy1y2y3data = zip(xdata, y1data, y2data, y3data)
    xy1y2y3data = sorted(xy1y2y3data)

    xdata = [n[0] for n in xy1y2y3data]
    y1data = [n[1] for n in xy1y2y3data]
    y2data = [n[2] for n in xy1y2y3data]
    y3data = [n[3] for n in xy1y2y3data]

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

    chartdata = {'x': xdata,
                 'name1': 'Amb Temp', 'y1': y1data, 'extra1': extra_serie1,
                 'name2': 'Beer Temp', 'y2': y2data, 'extra2': extra_serie2,
                 'name3': 'Amb Light', 'y3': y3data, 'extra3': extra_serie3}

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
            'chart_attr': {'color':['orange', 'blue', 'green']},
        }
    }
    return render_to_response('chart.html', data)
    