from monitor.models import Beer
from monitor.models import Reading
from monitor.models import Archive
from monitor.models import Config
from monitor.models import Event

import datetime
import pytz
        
def nowInUtc():
    utc = pytz.utc
    now = datetime.datetime.now(tz=utc)
    return now

'''Beer'''

def getAllBeer():
    all_beer = Beer.objects.all()
    return all_beer

'''Reading'''

def getAllReadings(cur_beer):
    '''Return all readings for cur_beer ordered by instant_actual'''
    active_readings = Reading.objects.filter(beer=cur_beer).order_by('-instant_actual_iso')
    return active_readings

def getLastReading(cur_beer):
    '''Returns the most recent reading for cur_beer if it exists'''
    readings = getAllReadings(cur_beer)
    if readings.count() == 0: last_read = None
    else: last_read = readings[:1].get()
    return last_read

def genReadingKey(cur_beer):
    reading_key = ''
    active_readings = getAllReadings(cur_beer) 
    for reading in active_readings:
        reading_key = reading_key + '^' + reading.get_unique_ident()
    return reading_key

def addReadingKey(reading):
    reading_key = ''
    reading_key = '^' + reading.get_unique_ident()
    return reading_key
    
'''Archive'''

def getAllArchives(cur_beer):
    all_archives = None
    try:
        all_archives = Archive.objects.filter(beer=cur_beer).order_by('-reading_date')
    finally:
        return all_archives

def getArchive(cur_beer, day):
    active_archive = None    
    try:
        active_archive = Archive.objects.get(beer=cur_beer, reading_date=day)
    finally:
        return active_archive

def getLastArchive(cur_beer):
    '''Returns the most recent archive for cur_beer if it exists'''
    archives = getAllArchives(cur_beer)
    if archives.count() == 0: last_archive = None
    else: last_archive = archives[:1].get()
    return last_archive

def createArchive(cur_beer, day):
    archive = None
    try:
        if not bool(getArchive(cur_beer, day)):
            archive = Archive(beer=cur_beer, reading_date=day)
            archive.update_instant = nowInUtc()
            archive.save()
    finally:
        return archive
    
def updateArchive(archive, reading):
    result = None
    try:
        archive.instant_actual += str(reading.get_instant_actual()) + '^'
        archive.light_amb += str(reading.get_light_amb()) + '^'
        archive.pres_beer += str(reading.get_pres_beer()) + '^'
        archive.temp_amb += str(reading.get_temp_amb()) + '^'
        archive.temp_beer += str(reading.get_temp_beer()) + '^'
        archive.event_temp_amb += str(reading.event_temp_amb.pk) + '^'
        archive.event_temp_beer += str(reading.event_temp_beer.pk) + '^'
        archive.update_instant = nowInUtc()
        archive.count += 1
        archive.save()
        reading.delete()
        result = True
    finally:
        return result

def genArchiveKey(cur_beer):
    archive_key = ''
    active_archives = getAllArchives(cur_beer)
    for archive in active_archives:
        archive_key = archive_key + '^' + archive.get_unique_ident()
    return archive_key

def addArchiveKey(archive):
    archive_key = ''
    archive_key = '^' + archive.get_unique_ident()
    return archive_key

'''Config'''

def getActiveConfig():
    active_config = Config.objects.filter()[:1].get()
    return active_config

def getActiveBeer():
    active_config = getActiveConfig()
    active_beer = active_config.beer
    return active_beer

def SetReadInstant(active_config):
    '''Set the current instant as active_config.read_last_instant'''
    right_now = nowInUtc()
    active_config.read_last_instant = right_now
    active_config.save()
    return

def getServerUrl():
    active_config = getActiveConfig()
    url = active_config.api_server_url
    return url
    
def getProdKey():
    active_config = getActiveConfig()
    key = active_config.api_prod_key
    return key    
    
def getTestKey():
    active_config = getActiveConfig()
    key = active_config.api_test_key
    return key
    
def getReadingKey():
    active_config = getActiveConfig()
    key = active_config.reading_key
    return key   
    
def getArchiveKey():
    active_config = getActiveConfig()
    key = active_config.archive_key
    return key

def setReadingKey(reading_key):
    active_config = getActiveConfig()
    active_config.reading_key = reading_key
    active_config.save()
    return None
    
def setArchiveKey(archive_key):
    active_config = getActiveConfig()
    active_config.archive_key = archive_key
    active_config.save()
    return None

def updateReadingKey():
    active_beer = getActiveBeer()
    reading_key = genReadingKey(active_beer)
    setReadingKey(reading_key)
    return None
    
def updateArchiveKey():
    active_beer = getActiveBeer()
    archive_key = genArchiveKey(active_beer)
    setArchiveKey(archive_key)
    return None        

def appendReadingKey(reading):
    reading_key = getReadingKey()
    reading_tail = addReadingKey(reading)
    reading_key = reading_key + reading_tail
    setReadingKey(reading_key)
    return None

def appendArchiveKey(archive):
    archive_key = getArchiveKey()
    archive_tail = addArchiveKey(archive)
    archive_key = archive_key + archive_tail
    setArchiveKey(archive_key)
    return None

'''Event'''

def createEvent(beer, reading, category, sensor, details):
    event = Event(beer=beer,reading=reading,category=category,sensor=sensor,details=details)
    event.save()
    if sensor == 'temp_amb':
        reading.event_temp_amb = event
        reading.save()
    elif sensor == 'temp_beer':
        reading.event_temp_beer = event
        reading.save()
    return event
    
def getEventData(reading=None,event_temp_amb=None,event_temp_beer=None):

    temp_beer_t = ''
    temp_beer_d = ''
    temp_amb_t = ''
    temp_amb_d = ''
    
    if bool(reading):
        temp_amb = reading.event_temp_amb
        temp_beer = reading.event_temp_beer
    elif bool(event_temp_amb) or bool(event_temp_beer):
        if bool(event_temp_amb):
            temp_amb = Event.objects.get(pk=event_temp_amb)
        if bool(event_temp_beer):
            temp_beer = Event.objects.get(pk=event_temp_beer)
        
    if bool(temp_amb):
        temp_amb_t = temp_amb.category
        temp_amb_d = temp_amb.details
    if bool(temp_beer):
        temp_beer_t = temp_beer.category
        temp_beer_d = temp_beer.details      
        
    return [temp_amb_t, temp_amb_d, temp_beer_t, temp_beer_d]