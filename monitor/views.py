from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext

from monitor.do import getActiveConfig, getActiveBeer, SetReadInstant, getProdKey, getTestKey
from monitor.do import getArchiveKey, getReadingKey, appendReadingKey
from monitor.do import getAllBeer
from monitor.do import getAllReadings, getLastReading
from monitor.do import getAllArchives, getLastArchive
from monitor.do import nowInUtc, createEvent, getEventData
from monitor.middleware import send2middleware
from monitor.models import Beer, Reading

from time import sleep
from datetime import timedelta
from postmark import PMMail
import datetime
import pytz

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
            instant_override = instant_override - (6*60*60)
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
            error = 'Sensor value of ' + str(round(value,2)) + ' outside range of ['
            error = error + str(lower) + ', ' + str(upper) + '] '
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
    beer = getActiveBeer() 
    category = 'Bounds'

    #Think about breaking these into arrays to simply adding more sensors
    error_cat = 'temp_amb'
    temp_amb_base = active_config.temp_amb_base
    temp_amb_dev = active_config.temp_amb_dev
    temp_amb = read.get_temp_amb()
    error = MaxMinCheck(temp_amb_base, temp_amb_dev, temp_amb, error_cat)
    [error_flag, error_details] = SetErrorInfo(error_flag, error_details, error)
    if bool(error):
        createEvent(beer, read, category, error_cat, error)   
        error = None

    error_cat = 'temp_beer'
    temp_beer_base = active_config.temp_beer_base
    temp_beer_dev = active_config.temp_beer_dev
    temp_beer = read.get_temp_beer()
    error = MaxMinCheck(temp_beer_base, temp_beer_dev, temp_beer, error_cat)
    [error_flag, error_details] = SetErrorInfo(error_flag, error_details, error)
    if bool(error):
        createEvent(beer, read, category, error_cat, error)   
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
    right_now = nowInUtc()
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

#C:\Python34\python -m pdb manage.py runserver
#Then press 'c'
#import pdb; pdb.set_trace()

@csrf_exempt
def api(request):

    key = stringFromPost(request, 'key')
    prod_key = getProdKey()
    test_key = getTestKey()
    if (key == prod_key) or (key == test_key):

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

            #Duplicate save from below for Event generation.
            #Need to save the Read so Event can link to it
            if key == prod_key:
                read.save()

            #Check for deviation errors
            error_flag = ErrorCheck(active_config, read)

            #And finally, save the record
            if key == prod_key:
                read.save()
                SetReadInstant(active_config)
                appendReadingKey(read)
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

@staff_member_required
def send_command(request, command_char=None):
    if command_char == None:
        command_status = str('')
    else:
        command_status = send2middleware(command_char)
    request.session['command_status'] = command_status
    return HttpResponseRedirect(reverse('commands'))

@staff_member_required
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

    return render_to_response('commands.html', data, context_instance=RequestContext(request))
    
def getAllData(cur_beer):
    '''Return a DF of reading/archive data, ordered by instant'''
    active_beer = getActiveBeer()    
    all_data = []
    archive_data = []
    reading_data = []
    archive_key = ''    
    reading_key = ''

    archive_key = getArchiveKey()
    cache_key = cache.get('archive_key')
    if (archive_key == cache_key) and (active_beer == cur_beer):
        archive_data = cache.get('archive_data')
    else:
        archive_key = ''
        active_archives = getAllArchives(cur_beer)
        for archive in active_archives:
            archive_key = archive_key + '^' + archive.get_unique_ident()
            instant_actual_arch = archive.get_instant_actual()
            temp_amb_arch = archive.get_temp_amb()
            temp_beer_arch = archive.get_temp_beer()
            light_amb_arch = archive.get_light_amb()
            pres_beer_arch = archive.get_pres_beer()
            event_temp_amb_arch = archive.get_event_temp_amb()
            event_temp_beer_arch = archive.get_event_temp_beer()
            counter = 0
            while counter < archive.count:
                event_temp_beer = event_temp_amb_arch[counter]
                event_temp_amb = event_temp_beer_arch[counter]
                [temp_amb_t, temp_amb_d, temp_beer_t, temp_beer_d] = getEventData(None,event_temp_beer,event_temp_amb)
                data = {'dt':instant_actual_arch[counter],
                        'temp_amb':[temp_amb_arch[counter],temp_amb_t,temp_amb_d],
                        'temp_beer':[temp_beer_arch[counter],temp_beer_t,temp_beer_d],
                        'light_amb':[light_amb_arch[counter],'undefined','undefined'],
                        'pres_beer':[pres_beer_arch[counter],'undefined','undefined'],
                }
                archive_data.append(data)
                counter += 1
        if active_beer == cur_beer:
            cache.set('archive_key', archive_key)
            cache.set('archive_data', archive_data)
    all_data = all_data + archive_data
    
    reading_key = getReadingKey()
    cache_key = cache.get('reading_key')
    if (reading_key == cache_key) and (active_beer == cur_beer):
        reading_data = cache.get('reading_data')
    else:
        reading_key = ''
        active_readings = getAllReadings(cur_beer) 
        for reading in active_readings:
            reading_key = reading_key + '^' + reading.get_instant_actual()
            
            [temp_amb_t, temp_amb_d, temp_beer_t, temp_beer_d] = getEventData(reading)

            data = {'dt':reading.get_instant_actual(),
                    'temp_amb':[reading.get_temp_amb(),temp_amb_t,temp_amb_d],
                    'temp_beer':[reading.get_temp_beer(),temp_beer_t,temp_beer_d],
                    'light_amb':[reading.get_light_amb(),'undefined','undefined'],
                    'pres_beer':[reading.get_pres_beer(),'undefined','undefined'],
            }
            reading_data.append(data)
        if active_beer == cur_beer:
            cache.set('reading_key', reading_key)
            cache.set('reading_data', reading_data)
    all_data = all_data + reading_data
    
    return all_data

def dashboard(request):
    '''Creates dashboard (gauges and table) page for the active beer'''
    active_config = getActiveConfig()
    active_beer = getActiveBeer()
    cur_reading = getLastReading(active_beer)

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
        "last_log_ago": get_date_diff(cur_reading.instant_actual, nowInUtc()),
        'all_beers': Beer.objects.all(),
        'active_beer': active_beer,
        'beer_date': active_beer.brew_date,
    }
    return render_to_response('dashboard.html',data)
def get_date_diff(d1,d2):
    '''Returns the difference between two datetime objects in a readable format'''
    diff = abs(d2-d1)

    if(diff.days > 0): out = str(diff.days) + " day(s) ago"
    elif(diff.seconds < 60): out = "less than a minute ago"
    elif(diff.seconds < 60*60): out = str(int(round(diff.seconds/60,0))) + " minute(s) ago"
    else: out = str(int(round(diff.seconds/(60*60),0))) + " hour(s) ago"

    return(out)
def get_paint_cols(val, rng = None):
    '''Returns the background color for a value given a set range. In the future, it could also return foreground color'''
    if rng == None or rng == (0,0): bgcol = "#FFFFFF" #White
    elif(rng[0] <= val <= rng[1]): bgcol = "#008000" #Green
    elif(not (rng[0] <= val <= rng[1])): bgcol = "#FF0000" #Red
    

    fgcol = "#000000" #Black
    return((bgcol, fgcol))
def dashboard_update(request):
    '''Forces a log then returns to dashboard page'''
    active_beer = getActiveBeer()
    old_reading = getLastReading(active_beer)

    for i in range(4):
        command_status = send2middleware("F")
        if command_status[0] == "Success": break
        sleep(.1)
    if command_status[0] == "Success":
        for i in range(49):
            if getLastReading(active_beer) != old_reading: break
            sleep(.1)
    return HttpResponseRedirect(reverse('dashboard')) 
def gen_unableToLoad(page_name, cur_beer):
    '''Creates a page saying the page_name for cur_berr was unable to be loaded due to no readings'''
    #In future: allow the message (reason for unable to load page) a parameter
    data = {
        'all_beers': Beer.objects.all(),
        'active_beer': getActiveBeer(),
        'page_name': page_name,
        'cur_beer': cur_beer,
    }
    return render_to_response('unabletoload.html',data)
def chart(request, cur_beer = None):
    '''Creates a chart page with the Google Annotation Chart'''
    #In future: send alerts too
    if cur_beer is None: cur_beer = getActiveBeer()
    else: cur_beer = Beer.objects.get(pk=cur_beer)
    active_beer = getActiveBeer()
    #active_beer is the system config active
    #cur_beer is the beer that is being charted    

    plot_data = getAllData(cur_beer)   
   
    last_read = getLastReading(cur_beer)
    last_archive = None
    
    if bool(last_read):
        start_date = getLastReading(cur_beer).instant_actual.date()
    else:
        last_archive = getLastArchive(cur_beer)
    
    if bool(last_archive):
        start_date = last_archive.reading_date
    else:
        start_date = datetime.date.today()
   
    #Get start_date which is 7 days before the last logged date.
    start_date = start_date - timedelta(days=7)   
    
    data = {
        'all_beers': Beer.objects.all(),
        'active_beer': active_beer,
        'cur_beer': cur_beer,
        'plot_data': plot_data,
        'beer_date': cur_beer.brew_date,
        'start_date': start_date.isoformat()
    }
    return render_to_response('chart.html', data)
def data_chk(request, page_name = "dashboard", cur_beer = None):
    '''Checks if we have readings for cur_beer then if page_name exists and then creates appropriate page'''
    if cur_beer is None: active_beer = getActiveBeer()
    else: active_beer = Beer.objects.get(pk=cur_beer)
    
    isData = False
    read_chk = getLastReading(active_beer)
    if bool(read_chk):
        isData = True
    else:
        arch_chk = getLastArchive(active_beer)
        if bool(arch_chk):
            isData = True
    
    if not bool(isData):
        out = gen_unableToLoad(page_name, active_beer)
    else:
        if page_name.upper() == "DASHBOARD": out = dashboard(request)
        elif page_name.upper() == "CHART": out = chart(request, cur_beer)
        else: out = "404 Page Not Found"
    
    return out
