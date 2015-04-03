from monitor.models import Reading
from monitor.get_config import getActiveBeer

def getAllReadings(active_beer):
    '''Return all readings for active_beer ordered by instant_actual'''
    active_readings = Reading.objects.filter(beer=active_beer).order_by('-instant_actual_iso')
    return active_readings

def getLastReading(active_beer):
    '''Returns the most recent reading for active_beer if it exists'''
    readings = getAllReadings(active_beer)
    if readings.count() == 0: last_read = None
    else: last_read = readings[:1].get()
    return last_read

def genReadingKey():
    active_beer = getActiveBeer()
    reading_key = ''
    
    active_readings = getAllReadings(active_beer) 
    for reading in active_readings:
        reading_key = reading_key + '^' + reading.get_unique_ident()

    return reading_key
