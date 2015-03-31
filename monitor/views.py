from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from monitor.archive import getAllArchives
from monitor.middleware import send2middleware
from monitor.models import Beer, Reading, Config

from time import sleep
from datetime import timedelta
from postmark import PMMail
import datetime

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

def getActiveConfig():
    active_config = Config.objects.filter()[:1].get()
    return active_config

def getActiveBeer():
    active_config = getActiveConfig()
    active_beer = active_config.beer
    return active_beer

def getAllBeer():
    all_beer = Beer.objects.all()
    return all_beer

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

    #Think about breaking these into arrays to simply adding more sensors
    error_cat = 'temp_amb'
    temp_amb_base = active_config.temp_amb_base
    temp_amb_dev = active_config.temp_amb_dev
    temp_amb = read.get_temp_amb()
    error = MaxMinCheck(temp_amb_base, temp_amb_dev, temp_amb, error_cat)
    [error_flag, error_details] = SetErrorInfo(error_flag, error_details, error)

    error_cat = 'temp_beer'
    temp_beer_base = active_config.temp_beer_base
    temp_beer_dev = active_config.temp_beer_dev
    temp_beer = read.get_temp_beer()
    error = MaxMinCheck(temp_beer_base, temp_beer_dev, temp_beer, error_cat)
    [error_flag, error_details] = SetErrorInfo(error_flag, error_details, error)

    read.error_flag = error_flag
    read.error_details = error_details
    return read.error_flag

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
    right_now = datetime.datetime.now()
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
        response['instant_actual'] = read.instant_actual
        response['error_flag'] = read.error_flag
        response['error_details'] = read.error_details
    return response

def SetReadInstant(active_config):
    '''Set the current instant as active_config.read_last_instant'''
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

        active_config = getActiveConfig()
        active_beer = getActiveBeer() #Get active beer

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

def send_command(request, command_char=None):
    if command_char == None:
        command_status = str('')
    else:
        command_status = send2middleware(command_char)
    request.session['command_status'] = command_status
    return HttpResponseRedirect(reverse('commands'))

def commands(request):
    blank = str('')
    command_status = blank
    error = blank
    details = blank

    if request.session.has_key('command_status'):
        command_status = request.session.get('command_status')
        del request.session['command_status']
        error = command_status[0]
        details = command_status[1]

    if not bool(error):
        error = blank
    if not bool(details):
        details = blank

    command_options = [('f','Force a log'),
                       ('m','Show log freq'),
                       ('m=1','Log freq = 1'),
                       ('m=5','Log freq = 5'),
                       ('m=15','Log freq = 15'),
                       ('m=30','Log freq = 30'),
                       ('r=temp_amb','Value of temp_amb'),
                       ('r=temp_beer','Value of temp_beer'),
                       ('r=light_amb','Value of light_amb'),
                       ('r=pres_beer','Value of pres_beer'),
                       ('l','Turn data collection on'),
                       ('o','Turn data collection off'),
                       ('d','Turn remote logging on'),
                       ('e','Turn remote logging off')
                      ]

    active_beer = getActiveBeer()
    all_beers = getAllBeer()
    beer_name = active_beer
    beer_date = active_beer.brew_date

    data = {
            'all_beers': all_beers,
            'beer_name': beer_name,
            'beer_date': beer_date,
            'active_beer': getActiveBeer(),
            'command_status': command_status,
            'command_options': command_options,
            'error': error,
            'details': details
           }

    return render_to_response('commands.html', data)

def getReadings(active_beer):
    '''Return all readings for active_beer ordered by instant_actual'''
    active_readings = Reading.objects.filter(beer=active_beer).order_by('instant_actual')
    return active_readings

def createDF(active_beer):
    '''Return a DF of reading/archive data, ordered by instant'''
    import pandas as pd
    import numpy as np

    df = pd.DataFrame(columns=['Instant', 'Temp Amb', 'Temp Beer', 'Light Amb'])
    #Add logic for instances where no data exists

    active_archives = getAllArchives(active_beer)
    for archive in active_archives:
        counter = 0
        instant_actual_a = archive.get_instant_actual()
        temp_amb_a = archive.get_temp_amb()
        temp_beer_a = archive.get_temp_beer()
        light_amb_a = archive.get_light_amb()

        #Remove loop and duplicate Readings grab below*************
        while counter < archive.count:
            instant_actual = instant_actual_a[counter]
            temp_amb = temp_amb_a[counter]
            temp_beer = temp_beer_a[counter]
            light_amb = light_amb_a[counter]
            counter += 1

            i = len(df) #Don't use this!    ***********************
            df.loc[i] = [instant_actual, temp_amb, temp_beer, light_amb]

    active_readings = getReadings(active_beer) 

    all_data = []
    for reading in active_readings:
        data = [reading.get_instant_actual(),reading.get_temp_amb(),reading.get_temp_beer(),reading.get_light_amb()]
        all_data.append(data)
                  
    glob_df = pd.DataFrame(all_data, columns=['Instant', 'Temp Amb', 'Temp Beer', 'Light Amb'])
    glob_df = df.sort('Instant')
    glob_df = df.reset_index(drop=True)
    df = glob_df

    return df

def dashboard(request):
    # To do:
    # -Add button to force a log and refresh page
    # -Add footnote of time of last log
    # -Function to find bgcol (and fgcol) and paint cells
    # -Add red and/or yellow ranges to gauges and cell painting

    active_config = getActiveConfig()
    active_beer = getActiveBeer()
    cur_reading = getReadings(active_beer).order_by("-instant_actual")[:1].get()

    cur_temp_amb = cur_reading.get_temp_amb()
    cur_temp_beer = cur_reading.get_temp_beer()
    cur_light_amb = cur_reading.get_light_amb()
    cur_pres_beer = cur_reading.get_pres_beer()

    if active_config.temp_amb_base != None and active_config.temp_amb_dev != None:
        temp_amb_rng = [active_config.temp_amb_base - active_config.temp_amb_dev, active_config.temp_amb_base + active_config.temp_amb_dev]
    else: temp_amb_rng = (0,0)
    if active_config.temp_beer_base != None and active_config.temp_beer_dev != None:
        temp_beer_rng = [active_config.temp_beer_base - active_config.temp_beer_dev, active_config.temp_beer_base + active_config.temp_beer_dev]
    else: temp_beer_rng = (0,0)

    data = {
        "vals": {
            "temp_amb": cur_temp_amb,
            "temp_beer": cur_temp_beer,
            "light_amb": cur_light_amb,
            "pres_beer": cur_pres_beer
        },
        "bgcols" : {
            "temp_amb": get_paint_cols(cur_temp_amb, temp_amb_rng)[0],
            "temp_beer": get_paint_cols(cur_temp_beer, temp_beer_rng)[0],
            "light_amb": get_paint_cols(cur_light_amb)[0],
            "pres_beer": get_paint_cols(cur_pres_beer)[0]
        },
        "greenrng": {
            "temp_amb": temp_amb_rng,
            "temp_beer": temp_beer_rng
        },
        "last_log_date": cur_reading.instant_actual.strftime("%Y-%m-%d"),
        "last_log_time": cur_reading.instant_actual.strftime("%H:%M:%S"),
        "last_log_ago": get_date_diff(cur_reading.instant_actual, datetime.datetime.now()),
        'all_beers': Beer.objects.all(),
        'active_beer': active_beer,
        'beer_date': active_beer.brew_date,
    }
    return render_to_response('dashboard.html',data)
def get_date_diff(d1,d2):
    diff = abs(d2-d1)

    if(diff.days > 0): out = str(diff.days) + " day(s) ago"
    elif(diff.seconds < 60): out = "less than a minute ago"
    elif(diff.seconds < 60*60): out = str(int(round(diff.seconds/60,0))) + " minute(s) ago"
    else: out = str(int(round(diff.seconds/(60*60),0))) + " hour(s) ago"

    return(out)
def get_paint_cols(val, rng = None):
    if rng == None or rng == (0,0): bgcol = "#FFFFFF" #White
    elif(rng[0] <= val <= rng[1]): bgcol = "#008000" #Green
    elif(not (rng[0] <= val <= rng[1])): bgcol = "#FF0000" #Red
    

    fgcol = "#000000" #Black
    return((bgcol, fgcol))
def dashboard_update(request):
    active_config = Config.objects.filter()[:1].get()
    active_beer = active_config.beer
    old_reading = Reading.objects.filter(beer=active_beer).order_by("-instant_actual")[:1].get()

    for i in range(4):
        command_status = send2middleware("F")
        if command_status[0] == "Success": break
        sleep(.1)
    if command_status[0] == "Success":
        for i in range(49):
            if Reading.objects.filter(beer=active_beer).order_by("-instant_actual")[:1].get() != old_reading: break
            sleep(.1)
    print(command_status[0])
    return HttpResponseRedirect(reverse('dashboard')) 
def gen_unableToLoad(page_name):
    data = {
        'all_beers': Beer.objects.all(),
        'active_beer': getActiveBeer(),
        'page_name': page_name,
    }
    return render_to_response('unabletoload.html',data)
def chart(request, cur_beer = None):
    if cur_beer is None: active_beer = getActiveBeer()
    else: active_beer = Beer.objects.get(pk=cur_beer)
    
    readings = getReadings(active_beer)
    plot_data = []
    for r in readings:
        add = {
                "dt":r.instant_actual.isoformat(),
                "temp_amb": [r.get_temp_amb(), 'undefined', 'undefined'],
                "temp_beer": [r.get_temp_beer(), 'undefined', 'undefined'],
                "light_amb": [r.get_light_amb(), 'undefined', 'undefined']
            }
        plot_data.append(add)
    
    data = {
        'all_beers': Beer.objects.all(),
        'active_beer': active_beer,
        'plot_data': plot_data,
        "beer_date": active_beer.brew_date,
    }
    return render_to_response('chart.html', data)
def data_chk(request, page_name, cur_beer = None):
    if cur_beer is None: active_beer = getActiveBeer()
    else: active_beer = Beer.objects.get(pk=cur_beer)
    
    read_chk = getReadings(active_beer)[:1]
    
    if(not bool(read_chk)): out = gen_unableToLoad(page_name)
    else:
        if page_name.upper() == "DASHBOARD": out = dashboard(request)
        elif page_name.upper() == "CHART": out = chart(request, cur_beer)
        else: out = "404 Page Not Found"
    
    return out