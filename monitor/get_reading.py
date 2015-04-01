from monitor.models import Reading

def getReadings(active_beer):
    '''Return all readings for active_beer ordered by instant_actual'''
    active_readings = Reading.objects.filter(beer=active_beer).order_by('-instant_actual_iso')
    return active_readings

def getLastReading(active_beer):
    '''Returns the most recent reading for active_beer if it exists'''
    last_read = None
    last_read = getReadings(active_beer)[:1].get()
    return last_read
