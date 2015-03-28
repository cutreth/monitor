from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from monitor.middleware import send2middleware
from monitor.models import Beer, Reading, Config

from time import sleep
from datetime import timedelta, datetime
from postmark import PMMail
import calendar, datetime

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

    message = PMMail(api_key = email_api_key, sender = email_sender,
                     to = email_to, subject = email_subject,
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
    request.session['command_status']= command_status                
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

def ConvertDateTime(obj):
    #Defunct after views.chart is removed
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
    #Plan to depricate this function
    all_beers = getAllBeer()

    if cur_beer is None:
        active_beer = getActiveBeer()
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
    
def graph(request,cur_beer=None):
    import mpld3 
        
    if cur_beer is None:
        active_beer = getActiveBeer()
    else:
        active_beer = Beer.objects.get(pk=cur_beer)
    
    all_beers = getAllBeer()
    beer_name = active_beer
    beer_date = active_beer.brew_date
    
    fig1=createFig(1, active_beer)
    fig2=createFig(2, active_beer)

    fig1_html = mpld3.fig_to_html(fig1)
    fig2_html = mpld3.fig_to_html(fig2)
    
    data = {
        'all_beers': all_beers,
        'beer_name': beer_name,
        'beer_date': beer_date,
        'active_beer': getActiveBeer(),
        'fig1': fig1_html,
        'fig2': fig2_html
    }
    
    return render_to_response('graph.html',data)

def createFig(vers, active_beer):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mpld
    import pandas as pd
    from mpld3 import plugins

    active_readings = Reading.objects.filter(beer=active_beer).order_by('instant_actual')
    instant_data = [mpld.date2num(n.instant_actual) for n in active_readings]
    
    x_count = len(active_readings)
    x_range = range(x_count)
    df = pd.DataFrame(index=x_range)
    df['Instant'] = instant_data

    fig, ax = plt.subplots()
    ax.grid(True, alpha=0.3)
        
    # Define some CSS to control our custom labels
    css = """
    table
    {
      border-collapse: collapse;
    }
    th
    {
      color: #ffffff;
      background-color: #000000;
    }
    td
    {
      background-color: #cccccc;
    }
    table, th, td
    {
      font-family:Arial, Helvetica, sans-serif;
      border: 1px solid black;
      text-align: right;
    }
    """        
        
    if vers==1:
        temp_amb_data = [n.get_temp_amb() for n in active_readings]
        df['Temp Amb'] = temp_amb_data        
        y_temp_amb = ax.plot_date(df['Instant'],df['Temp Amb'],'b.-',label='Temp Amb')   
        ax.set_ylabel('Temp')      
        title = str(active_beer) + ' - Temp'

    if vers==1:
        temp_beer_data = [n.get_temp_beer() for n in active_readings]
        df['Temp Beer'] = temp_beer_data
        y_temp_beer = ax.plot_date(df['Instant'],df['Temp Beer'],'r.-',label='Temp Beer')
        ax.set_ylabel('Temp')
        title = str(active_beer) + ' - Temp'
        
    if vers==2:
        light_amb_data = [n.get_light_amb() for n in active_readings]
        df['Light Amb'] = light_amb_data
        y_light_amb = ax.plot_date(df['Instant'],df['Light Amb'],'y.-',label='Light Amb')  
        ax.set_ylabel('Light') 
        title = str(active_beer) + ' - Light' 

    instant_data = [mpld.num2date(n).strftime('%Y-%m-%d %H:%M') for n in instant_data]
    df.drop('Instant',axis=1,inplace=True)    
    
    #Create chart labels
    labels = []   
    for i in range(x_count):
        label = df.ix[[i], :].T
        label.columns = [instant_data[i]]
        # .to_html() is unicode; so make leading 'u' go away with str()
        labels.append(str(label.to_html()))   

    if vers==1:
        tooltip = plugins.PointHTMLTooltip(y_temp_amb[0], labels,
                                   voffset=10, hoffset=10, css=css)
        plugins.connect(fig, tooltip)   

    if vers==1:
        tooltip2 = plugins.PointHTMLTooltip(y_temp_beer[0], labels,
                                   voffset=10, hoffset=10, css=css)
        plugins.connect(fig, tooltip2)
        
    if vers==2:
        tooltip = plugins.PointHTMLTooltip(y_light_amb[0], labels,
                                   voffset=10, hoffset=10, css=css)
        plugins.connect(fig, tooltip)   

    ax.set_xlabel('Instant')   
    ax.set_title(title, size=20)        
    ax.legend(loc='best', fancybox=True, framealpha=0.5, title='')  
    
    return fig
    
def dashboard(request):
    # To do:
    # -Add button to force a log and refresh page
    # -Add footnote of time of last log
    # -Function to find bgcol (and fgcol) and paint cells
    # -Add red and/or yellow ranges to gauges and cell painting
    
    active_config = Config.objects.filter()[:1].get()
    active_beer = active_config.beer
    
    cur_reading = Reading.objects.filter(beer=active_beer).order_by("-instant_actual")[:1].get()
    
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
        'active_beer': getActiveBeer(),
    }
    
    return render_to_response('dashboard.html',data)
def get_date_diff(d1,d2):
    diff = abs(d2-d1)

    if(diff.days > 0): out = str(diff.days) + " day(s) ago"
    elif(diff.seconds < 1): out = "now"
    elif(diff.seconds < 60): out = str(round(diff.seconds,0)) + " second(s) ago"
    elif(diff.seconds < 60*60): out = str(round(diff.seconds/60,1)) + " minute(s) ago"
    else: out = str(round(diff.seconds/(60*60),1)) + " hour(s) ago"
    
    return(out)
def get_paint_cols(val, rng = None):
    if rng == None: bgcol = "#FFFFFF" #White
    elif(rng[0] <= val <= rng[1]): bgcol = "#008000" #Green
    else: bgcol = "#FF0000" #Red
    
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
