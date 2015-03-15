from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from monitor.models import Beer, Reading, Config

from datetime import timedelta
import datetime

@csrf_exempt
def api(request):

    key = request.POST.get('key')
    if key == 'beer':

        active_config = Config.objects.get(pk=1)
        active_beer = active_config.beer
        read = Reading(beer=active_beer)

        light_amb = float(request.POST.get('light_amb',0))
        temp_beer = float(request.POST.get('temp_beer',0))
        temp_amb = float(request.POST.get('temp_amb',0))

        if (light_amb>0 or temp_beer>0 or temp_amb>0):

            read.light_amb = light_amb
            read.temp_beer = temp_beer
            read.temp_amb = temp_amb

            temp_unit = request.POST.get('temp_unit','F')
            temp_unit = str(temp_unit)
            temp_unit = temp_unit.capitalize()[0]
            if temp_unit == 'F' or temp_unit == 'C':
                read.temp_unit = temp_unit

            error_flag = DeviationCheck(active_config, active_beer, read)
            
            instant_override = request.POST.get('instant_override',None)            
            if bool(instant_override):
                instant_override = int(instant_override)
                instant_override=datetime.datetime.fromtimestamp(instant_override)
                read.instant_override = instant_override          
            

            read.save()

            from postmark import PMMail

            #C:\Python34\python -m pbd manage.py runserver
            #import pdb; pdb.set_trace()

            email_api_key = '8912d7b5-aa44-472f-bef9-2519cb3befa8'
            
            email_sender = "cutreth@cutreth.com"
            email_to = "kikot.world@gmail.com"
            
            email_subject = "A beer update!"
            email_text_body = read.error_details

            if error_flag:
                message = PMMail(api_key = email_api_key,
                                 sender = email_sender,
                                 to = email_to,
                                 subject = email_subject,
                                 text_body = email_text_body)                                
                message.send()



            response = HttpResponse("Success")
            response['light_amb'] = light_amb
            response['temp_beer'] = temp_beer
            response['temp_amb'] = temp_amb
            response['temp_unit'] = temp_unit
            response['instant_override'] = instant_override
            return response

        else:
            response = HttpResponse("Failure")
            response['light_amb'] = light_amb
            response['temp_beer'] = temp_beer
            response['temp_amb'] = temp_amb
            return response

    else:
        return HttpResponse("Key failure")        



def DeviationCheck(active_config, active_beer, read):

    #Enhance to add support for temperature conversions
    temp_amb_base = active_config.temp_amb_base
    temp_amb_dev = active_config.temp_amb_dev

    temp_beer_base = active_config.temp_beer_base
    temp_beer_dev = active_config.temp_beer_dev

    if (bool(temp_amb_base) and bool(temp_amb_dev)):
        temp_amb_max = temp_amb_base + temp_amb_dev
        temp_amb_min = temp_amb_base - temp_amb_dev
        
        if not (temp_amb_min < read.temp_amb < temp_amb_max):
            read.error_flag = True
            read.error_details = read.error_details + 'temp_amb: [' + str(temp_amb_min) + ', ' + str(temp_amb_max) + ']'
            read.error_details = read.error_details + ' *[' + str(read.temp_amb) + '] '        
        elif read.error_flag is None:
            read.error_flag = False

    if (bool(temp_beer_base) and bool(temp_beer_dev)):
        temp_beer_max = temp_beer_base + temp_beer_dev
        temp_beer_min = temp_beer_base - temp_beer_dev
        
        if not (temp_beer_min < read.temp_beer < temp_beer_max):
            read.error_flag = True
            read.error_details = read.error_details + 'temp_beer: [' + str(temp_beer_min) + ', ' + str(temp_beer_max) + ']'
            read.error_details = read.error_details + ' *[' + str(read.temp_beer) + '] '
        elif read.error_flag is None:
            read.error_flag = False
    
    return read.error_flag


def ConvertDateTime(obj):
    import calendar, datetime

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

    xdata = [ConvertDateTime(n.instant_actual()) for n in active_readings]
    temp_amb_data = [n.get_temp_amb() for n in active_readings]
    temp_beer_data = [n.get_temp_beer() for n in active_readings]
    light_amb_data = [n.light_amb for n in active_readings]

    #Doesn't respect ordering via Reading.instant_actual()
    error_readings = Reading.objects.filter(beer=active_beer).filter(error_flag=True)

    y1data=temp_amb_data
    y2data=temp_beer_data
    #nothing = light_amb_data


    xdata.append(min(xdata)-1)
    y1data.append(float(90))
    y2data.append(float(50))

    xy1y2data = zip(xdata, y1data, y2data)
    xy1y2data = sorted(xy1y2data)

    xdata = [n[0] for n in xy1y2data]
    y1data = [n[1] for n in xy1y2data]
    y2data = [n[2] for n in xy1y2data]

    beer_name = active_beer
    beer_date = active_beer.brew_date


    ydata=y1data
    ydata2=y2data

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
    chartdata = {'x': xdata,
                 'name1': 'Amb Temp', 'y1': ydata, 'extra1': extra_serie1,
                 'name2': 'Beer Temp', 'y2': ydata2, 'extra2': extra_serie2}

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
            'chart_attr': {'color':['orange', 'blue']},
        }
    }
    return render_to_response('chart.html', data)
