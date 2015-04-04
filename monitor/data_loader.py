from monitor.models import Beer, Reading
from monitor.views import getActiveBeer
from datetime import datetime, timedelta
import random

def gen_fake_data(n, beer=None):
    if beer == None:
        beer = getActiveBeer()
    
    #Add readings to beer
    for i in range(n):
        r = Reading(beer = beer,
                    light_amb = random.normalvariate(100, 20),
                    pres_beer = random.normalvariate(150, 20),
                    temp_amb = random.normalvariate(70, 2),
                    temp_beer = random.normalvariate(70, 2)
                )
        r.save()

def create_or_modify(beer_name,date):
    beer = Beer.objects.filter(beer_text=beer_name)
    if bool(beer):
        beer = beer.get()
    else:
        beer = Beer(beer_text=beer_name, brew_date=date)
        beer.save()
    return beer
        
def gen_blank_beer():
    now = datetime.now()
    name = 'Blank Beer'
    beer = create_or_modify(name,now)
    
    readings = Reading.objects.filter(beer=beer)
    readings.delete()

def gen_two_weeks():
    now = datetime.now()
    name = "Two Weeks"
    beer = create_or_modify(name,now)    
    
    cur_datetime = now - timedelta(days = 14)
    while(cur_datetime <= now):
        r = Reading(beer = beer,
                instant_override = cur_datetime,
                light_amb = random.normalvariate(100, 10),
                pres_beer = random.normalvariate(50, 5),
                temp_amb = random.normalvariate(70, 2),
                temp_beer = random.normalvariate(72, 1)
            )
        r.save()
        cur_datetime = cur_datetime + timedelta(seconds = 60*15)