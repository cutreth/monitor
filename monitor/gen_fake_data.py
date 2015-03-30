from monitor.models import Beer, Reading
import random

def gen_fake_data(beer_name, n):
    #Create new beer
    b = Beer(beer_text = beer_name)
    b.save()
    
    #Add readings to beer
    for i in range(n):
        r = Reading(beer = b,
                    light_amb = random.normalvariate(100, 20),
                    pres_beer = random.normalvariate(150, 20),
                    temp_amb = random.normalvariate(70, 2),
                    temp_beer = random.normalvariate(70, 2)
                )
        r.save()

gen_fake_data("Tons of Readings", 5000)