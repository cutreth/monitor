from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

import monitor.api as api
import monitor.do as do
from monitor.models import Beer, Reading
from monitor.middleware import send2middleware

import datetime
from datetime import timedelta
from time import sleep

#C:\Python34\python -m pdb manage.py runserver
#Then press 'c'
#import pdb; pdb.set_trace()

@csrf_exempt
def api_in(request):

    key = api.stringFromPost(request, 'key')
    prod_key = do.getProdKey()
    test_key = do.getTestKey()
    if (key == prod_key) or (key == test_key):

        active_config = do.getActiveConfig()
        active_beer = do.getActiveBeer() #Get active beer

        read = Reading(beer=active_beer) #Create reading record

        #Populate sensor data
        light_amb = api.floatFromPost(request, 'light_amb')
        pres_beer = api.floatFromPost(request, 'pres_beer')
        temp_beer = api.floatFromPost(request, 'temp_beer')
        temp_amb = api.floatFromPost(request, 'temp_amb')

        sensor_data = [light_amb, pres_beer, temp_amb, temp_beer]

        if not api.allDataBlank(sensor_data) and api.allDataPositive(sensor_data):

            #Get beer-level modifiers
            light_amb_mod = active_beer.get_light_amb_mod()
            pres_beer_mod = active_beer.get_pres_beer_mod()
            temp_beer_mod = active_beer.get_temp_beer_mod()
            temp_amb_mod = active_beer.get_temp_amb_mod()

            #Store unmodified values
            read.light_amb_orig = light_amb
            read.pres_beer_orig = pres_beer
            read.temp_beer_orig = temp_beer
            read.temp_amb_orig = temp_amb

            #All data set for every read
            read.light_amb = do.applyModifier(light_amb,light_amb_mod)
            read.pres_beer = do.applyModifier(pres_beer,pres_beer_mod)
            read.temp_beer = do.applyModifier(temp_beer,temp_beer_mod)
            read.temp_amb = do.applyModifier(temp_amb,temp_amb_mod)

            #Get and set temp_unit
            temp_unit = api.getTempUnit(request)
            read.temp_unit = temp_unit

            #Get and set instant_override if it exists
            instant_override = api.getInstantOverride(request) #0 = NULL
            if bool(instant_override):
                read.instant_override = instant_override
            #instant_override will either be 0 or a datetime object

            #Duplicate save from below for Event generation.
            #Need to save the Read so Event can link to it
            if key == prod_key:
                read.save()

            #Check for deviation errors
            error_flag = api.BoundsErrorCheck(active_config, read)

            #And finally, save the record
            if key == prod_key:
                read.save()
                do.setReadInstant(active_config)
                do.appendReadingKey(read)
                if error_flag: #Send error emails if necessary
                    message = api.BuildErrorEmail(active_config, read, None)
                    api.SendErrorEmail(active_config, message)
                status = "Success"
            else:
                status = "Test Success"
        else:
            status = "Data Failure"
    else:
        status = "Key Failure"
        read = None #Not otherwise set outside the for loop

    #Generate and send a response per status flag with 'read' object data
    response = api.createHttpResp(read, status)
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

    active_beer = do.getActiveBeer()
    all_beers = do.getAllBeer()
    beer_name = active_beer
    beer_date = active_beer.brew_date

    data = {
            'all_beers': all_beers,
            'beer_name': beer_name,
            'beer_date': beer_date,
            'active_beer': do.getActiveBeer(),
            'command_status': command_status,
            'command_options': command_options,
            'error': error,
            'details': details
           }

    return render_to_response('commands.html', data, context_instance=RequestContext(request))

def dashboard(request):
    '''Creates dashboard (gauges and table) page for the active beer'''
    active_config = do.getActiveConfig()
    active_beer = do.getActiveBeer()
    cur_reading = do.getLastReading(active_beer)

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
        "last_log_ago": get_date_diff(cur_reading.instant_actual, do.nowInUtc()),
        "next_log": next_log_estimate(),
        "all_beers": Beer.objects.all(),
        "active_beer": active_beer,
        "beer_date": active_beer.brew_date,
    }
    return render_to_response('dashboard.html',data)

def get_date_diff(d1,d2, append = "ago"):

    '''Returns the difference between two datetime objects in a readable format'''
    diff = abs(d2-d1)

    if(diff.days > 0): out = str(diff.days) + " day(s)"
    elif(diff.seconds < 60): out = "less than a minute"
    elif(diff.seconds < 60*60): out = str(int(round(diff.seconds/60,0))) + " minute(s)"
    else: out = str(int(round(diff.seconds/(60*60),0))) + " hour(s)"

    if append != None: out = out + " " + append
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
    active_beer = do.getActiveBeer()
    old_reading = do.getLastReading(active_beer)

    for i in range(4):
        command_status = send2middleware("F")
        if command_status[0] == "Success": break
        sleep(.1)
    if command_status[0] == "Success":
        for i in range(49):
            if do.getLastReading(active_beer) != old_reading: break
            sleep(.1)
    return HttpResponseRedirect(reverse('dashboard'))

def gen_unableToLoad(page_name, cur_beer):
    '''Creates a page saying the page_name for cur_berr was unable to be loaded due to no readings'''
    #In future: allow the message (reason for unable to load page) a parameter
    data = {
        'all_beers': Beer.objects.all(),
        'active_beer': do.getActiveBeer(),
        'page_name': page_name,
        'cur_beer': cur_beer,
    }
    return render_to_response('unabletoload.html',data)

def chart(request, cur_beer = None):
    '''Creates a chart page with the Google Annotation Chart'''
    #In future: send alerts too
    if cur_beer is None: cur_beer = do.getActiveBeer()
    else: cur_beer = Beer.objects.get(pk=cur_beer)
    active_beer = do.getActiveBeer()
    #active_beer is the system config active
    #cur_beer is the beer that is being charted

    plot_data = do.getAllData(cur_beer)

    last_read = do.getLastReading(cur_beer)
    last_archive = None

    if bool(last_read):
        start_date = do.getLastReading(cur_beer).instant_actual.date()
    else:
        last_archive = do.getLastArchive(cur_beer)

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
    if cur_beer is None: active_beer = do.getActiveBeer()
    else: active_beer = Beer.objects.get(pk=cur_beer)

    isData = False
    read_chk = do.getLastReading(active_beer)
    if bool(read_chk):
        isData = True
    else:
        arch_chk = do.getLastArchive(active_beer)
        if bool(arch_chk):
            isData = True

    if not bool(isData):
        out = gen_unableToLoad(page_name, active_beer)
    else:
        if page_name.upper() == "DASHBOARD": out = dashboard(request)
        elif page_name.upper() == "CHART": out = chart(request, cur_beer)
        else: out = "404 Page Not Found"

    return out
def next_log_estimate():
    last_reading = do.getLastReading(do.getActiveBeer()).instant_actual
    log_freq = None
    for i in range(10):
        r, msg = send2middleware("M")
        print(r)
        if r.upper() == "SUCCESS":
            log_freq = int(msg.split("=")[1])
            break
        sleep(.1)
    out = "unknown amount of time"
    if log_freq != None:
        next = last_reading + timedelta(minutes = log_freq)
        now = do.nowInUtc()
        if next >= now: out = get_date_diff(do.nowInUtc(), next, append = None)
    return(out)
