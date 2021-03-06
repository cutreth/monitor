import monitor.api as api
import monitor.do as do
from monitor.models import Beer, Reading

from datetime import timedelta
from random import normalvariate

def gen_fake_data(n, beer=None):
    if beer == None:
        beer = do.getActiveBeer()
    active_config = do.getActiveConfig()

    #Add readings to beer
    for i in range(n):
        r = Reading(beer = beer,
                    light_amb = normalvariate(100, 20),
                    pres_beer = normalvariate(150, 20),
                    temp_amb = normalvariate(70, 2),
                    temp_beer = normalvariate(70, 2)
                )
        r.save()
        api.BoundsErrorCheck(active_config, r)

def create_or_modify(beer_name,date):
    beer = Beer.objects.filter(beer_text=beer_name)
    if bool(beer):
        beer = beer.get()
    else:
        beer = Beer(beer_text=beer_name, brew_date=date)
        beer.save()
    return beer

def gen_blank_beer():
    now = do.nowInUtc()
    name = 'Blank Beer'
    beer = create_or_modify(name,now)

    readings = Reading.objects.filter(beer=beer)
    readings.delete()

def gen_two_weeks():
    now = do.nowInUtc()
    name = "Two Weeks"
    beer = create_or_modify(name,now)

    cur_datetime = now - timedelta(days = 14)
    while(cur_datetime <= now):
        r = Reading(beer = beer,
                instant_override = cur_datetime,
                light_amb = normalvariate(100, 10),
                pres_beer = normalvariate(50, 5),
                temp_amb = normalvariate(70, 2),
                temp_beer = normalvariate(72, 1)
            )
        r.save()
        cur_datetime = cur_datetime + timedelta(seconds = 60*15)