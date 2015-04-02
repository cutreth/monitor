from monitor.models import Beer, Reading
from datetime import datetime, timedelta
import random

now = datetime.now()

'''Blank Beer'''
#b1 = Beer.objects.filter(beer_text = "Blank Beer")
#b1.delete()
#b1 = Beer(beer_text = "Blank Beer", brew_date = now)
#b1.save()

'''2 weeks of data'''
b2 = Beer.objects.filter(beer_text = "Two weeks of readings").get()
Reading.objects.filter(beer=b2).delete()

cur_datetime = now - timedelta(days = 14)
while(cur_datetime <= now):
    r = Reading(beer = b2,
            instant_override = cur_datetime,
            light_amb = random.normalvariate(100, 10),
            pres_beer = random.normalvariate(50, 5),
            temp_amb = random.normalvariate(70, 2),
            temp_beer = random.normalvariate(72, 1)
        )
    r.save()
    cur_datetime = cur_datetime + timedelta(seconds = 60*15)