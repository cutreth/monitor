from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from monitor.models import Beer, Reading, Config

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
    
            temp_beer = request.POST.get('temp_beer')
            temp_amb = request.POST.get('temp_amb')
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
        

def chart(request):
    xdata = ["Apple", "Apricot", "Avocado", "Banana", "Boysenberries", "Blueberries", "Dates", "Grapefruit", "Kiwi", "Lemon"]
    ydata = [52, 48, 160, 94, 75, 71, 490, 82, 46, 17]
    chartdata = {'x': xdata, 'y': ydata}
    charttype = "pieChart"
    chartcontainer = 'piechart_container'
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return render_to_response('chart.html', data)