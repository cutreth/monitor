from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

import monitor.api as api
import monitor.do as do
from monitor.models import Beer, Reading
from monitor.middleware import sendCommand

import re
import csv
from datetime import timedelta, datetime
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
def commands(request):
    blank = str('')
    command_status = blank
    error = blank
    details = blank
    command = request.GET.copy()

    if command:
        if command["code"].lower() == "s": command["time"] = datetime.utcnow().timestamp()
        command_status = sendCommand(command.urlencode())
        error = command_status[0]
        details = command_status[1]

    #List vars: [Current Value, Alert, Cell Color (for future use)]
    varlist = {
                "temp_amb":["?", "?", "#FFFFFF"],
                "temp_beer":["?", "?", "#FFFFFF"],
                "light_amb":["?", "?", "#FFFFFF"],
                "pres_beer":["?", "?", "#FFFFFF"]
            }


    active_beer = do.getActiveBeer()
    all_beers = do.getAllBeer()
    beer_name = active_beer
    beer_date = active_beer.brew_date

    s, log_freq = sendCommand("?code=m")
    if s != "Success": log_freq = "?"
    else: log_freq = log_freq.split("=")[1]

    collection_status = do.getStatus("?code=c&dir=get")
    logging_status = do.getStatus("?code=L&dir=get")

    sleep(.1)
    s, alert_res = sendCommand("?code=A&var=get")
    if s == "Success":
        if "off" not in alert_res:
            re_alert = re.search("(.*)(\[\d+, \d+\])", alert_res.split(":")[1], re.IGNORECASE)
            alert_var = re_alert.group(1)
            alert_rng = re_alert.group(2)
        else: alert_var = None
    else: alert_var = "?"

    for var in varlist:
        sleep(.1)
        s, val = sendCommand("?code=r&var=" + var)
        if s == "Success":
            varlist[var][0] = val.split(":")[1]
        if alert_var != "?":
            if alert_var == var: varlist[var][1] = str(alert_rng)
            else: varlist[var][1] = "Set alert"

    data = {
            'all_beers': all_beers,
            'beer_name': beer_name,
            'beer_date': beer_date,
            'active_beer': do.getActiveBeer(),
            'command_status': command_status,
            'varlist': varlist,
            'error': error,
            'details': details,
            'log_freq': log_freq,
            'collection_status': collection_status,
            'logging_status': logging_status,
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
            "temp_amb": do.get_paint_cols(cur_temp_amb, temp_amb_rng)[0],
            "temp_beer": do.get_paint_cols(cur_temp_beer, temp_beer_rng)[0],
            "light_amb": do.get_paint_cols(cur_light_amb)[0],
            "pres_beer": do.get_paint_cols(cur_pres_beer)[0]
        },
        "greenrng": {
            "temp_amb": temp_amb_rng,
            "temp_beer": temp_beer_rng
        },
        "last_log_date": cur_reading.instant_actual.strftime("%Y-%m-%d"),
        "last_log_time": cur_reading.instant_actual.strftime("%H:%M:%S"),
        "last_log_ago": do.get_date_diff(cur_reading.instant_actual, do.nowInUtc()),
        "next_log": do.next_log_estimate(),
        "all_beers": Beer.objects.all(),
        "active_beer": active_beer,
        "beer_date": active_beer.brew_date,
    }
    return render_to_response('dashboard.html',data)

def dashboard_update(request):
    '''Forces a log then returns to dashboard page'''
    active_beer = do.getActiveBeer()
    old_reading = do.getLastReading(active_beer)

    command_status = sendCommand("?code=F")
    if command_status[0] == "Success":
        '''Wait until the forced log actually shows up in django'''
        for i in range(49):
            if do.getLastReading(active_beer) != old_reading: break
            sleep(.1)
    return HttpResponseRedirect(reverse('dashboard'))

def chart(request, cur_beer = None):
    '''Creates a chart page with the Google Annotation Chart'''
    #In future: send alerts too
    if cur_beer is None: cur_beer = do.getActiveBeer()
    else: cur_beer = Beer.objects.get(pk=cur_beer)
    active_beer = do.getActiveBeer()
    #active_beer is the system config active
    #cur_beer is the beer that is being charted

    plot_data= do.getAllData(cur_beer)

    last_read = do.getLastReading(cur_beer)
    last_archive = None
    end_date = None

    if bool(last_read):
        end_date = do.getLastReading(cur_beer).instant_actual.date()
    else:
        last_archive = do.getLastArchive(cur_beer)
        if bool(last_archive):
            end_date = last_archive.reading_date
    
    today = do.nowInUtc().date()
    if bool(end_date):
        end_date = end_date + timedelta(days=1)
    else:
        end_date = today
    
    start_date = end_date - timedelta(days=7)     
    start_date = start_date.isoformat()
    if end_date == today:
        end_date = None
    elif bool(end_date):
        end_date = end_date.isoformat()

    data = {
        'all_beers': Beer.objects.all(),
        'active_beer': active_beer,
        'cur_beer': cur_beer,
        'plot_data': plot_data,
        'beer_date': cur_beer.brew_date,
        'start_date': start_date,
        'end_date': end_date,
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
    
def export(request):
    '''Exports archived data'''
    try: cur_beer = Beer.objects.get(pk=request.GET["beerid"])
    except: cur_beer = do.getActiveBeer()
    #Get data
    vars, all_data = do.getExportData(cur_beer)
    #Get meta data (exporting two files, how? zip them?)

    #Make csv and HTTP response
    fname = cur_beer.beer_text + ".csv"
    r = HttpResponse(content_type = "text/csv")
    r["Content-Disposition"] = "attachment; filename = '" + fname + "'"
    writer = csv.DictWriter(r, vars)
    writer.writeheader()
    for row in all_data: writer.writerow(row)
    return(r)