from monitor.models import Beer,Reading
from monitor.views import getActiveBeer
from random import normalvariate
from datetime import datetime, timedelta

def gen_fake_data(n, beer=None):
    if beer == None:
        beer = getActiveBeer()
    
    #Add readings to beer
    for i in range(n):
        r = Reading(beer = beer,
                    light_amb = normalvariate(100, 20),
                    pres_beer = normalvariate(150, 20),
                    temp_amb = normalvariate(70, 2),
                    temp_beer = normalvariate(70, 2)
                )
        r.save()

def gen_beers(two_weeks = True, blank_beer = False):
    now = datetime.now()
    '''Blank Beer'''
    if(bank_beer == True):
        b1 = Beer.objects.filter(beer_text = "Blank Beer")
        b1.delete()
        b1 = Beer(beer_text = "Blank Beer", brew_date = now)
        b1.save()

    '''2 weeks of data'''
    if(two_weeks == True):
        b2 = Beer.objects.filter(beer_text = "Two weeks of readings").get()
        Reading.objects.filter(beer=b2).delete()

        cur_datetime = now - timedelta(days = 14)
        while(cur_datetime <= now):
            r = Reading(beer = b2,
                    instant_override = cur_datetime,
                    light_amb = normalvariate(100, 10),
                    pres_beer = normalvariate(50, 5),
                    temp_amb = normalvariate(70, 2),
                    temp_beer = normalvariate(72, 1)
                )
            r.save()
            cur_datetime = cur_datetime + timedelta(seconds = 60*15)