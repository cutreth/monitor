from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from monitor.models import Beer, Reading, Config

import random
import datetime
from datetime import timedelta

def index(request):
    return HttpResponse("Hello, world. You're at the index.")
    
def success(request):
    return HttpResponse("Success")

def fail(request):
    return HttpResponse("Fail")
    
@csrf_exempt
def api(request):
    try:
        key = request.POST.get('key')
        if key == 'beer':
            
            active_config = Config.objects.get(pk=1)
            active_beer = active_config.beer
            read = Reading(beer=active_beer)
    
            light_amb = request.POST.get('light_amb')
            temp_beer = request.POST.get('temp_beer')
            temp_amb = request.POST.get('temp_amb')
            read.light_amb = light_amb
            read.temp_beer = temp_beer
            read.temp_amb = temp_amb
        
            temp_unit = str(request.POST.get('temp_unit'))
            temp_unit = temp_unit.capitalize()[0]
            read.temp_unit = temp_unit
    
            read.save()
            return HttpResponseRedirect(reverse('success'))
        
        else:
            return HttpResponseRedirect(reverse('fail'))
    except:
        return HttpResponseRedirect(reverse('index'))

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
    

def chart(request):
    
    active_config = Config.objects.get(pk=1)
    active_beer = active_config.beer
    active_readings = Reading.objects.filter(beer=active_beer)

    xdata = [ConvertDateTime(n.instant_actual()) for n in active_readings]
    y1data = [n.get_temp_amb() for n in active_readings]    
    y2data = [n.get_temp_beer() for n in active_readings]   
    
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
    
    """
    lineChart page
    """
    """
    start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
    nb_element = 150
    xdata = range(nb_element)
    xdata = list(map(lambda x: start_time + x * 1000000000, xdata))
    ydata = [i + random.randint(1, 10) for i in range(nb_element)]
    ydata2 = list(map(lambda x: x * 2, ydata))
    """

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


def linechart(request):
    """
    lineChart page
    """
    start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
    nb_element = 150
    xdata = range(nb_element)
    xdata = list(map(lambda x: start_time + x * 1000000000, xdata))
    ydata = [i + random.randint(1, 10) for i in range(nb_element)]
    ydata2 = list(map(lambda x: x * 2, ydata))

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie1 = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "date_format": tooltip_date,
        'color': '#a4c639'
    }
    extra_serie2 = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "date_format": tooltip_date,
        'color': '#FF8aF8'
    }
    chartdata = {'x': xdata,
                 'name1': 'series 1', 'y1': ydata, 'extra1': extra_serie1,
                 'name2': 'series 2', 'y2': ydata2, 'extra2': extra_serie2}

    charttype = "lineChart"
    chartcontainer = 'linechart_container'  # container name
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': True,
            'x_axis_format': '%d %b %Y %H',         
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return render_to_response('linechart.html', data)