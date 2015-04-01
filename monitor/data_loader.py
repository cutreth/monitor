from monitor.models import Reading
from monitor.views import getActiveBeer
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
