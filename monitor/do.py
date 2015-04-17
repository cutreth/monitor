from django.core.cache import cache

from monitor.models import Beer
from monitor.models import Reading
from monitor.models import Archive
from monitor.models import Config
from monitor.models import Event

from monitor.middleware import send2middleware

from datetime import timedelta
from time import sleep
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

def applyModifier(val,mod=None):
    try:
        if bool(mod):
            for item in mod:
                split = item.split('|')
                operator = str(split[0])
                constant = float(split[1])
                if operator == '-':
                    constant = -1 * constant
                    operator = '+'
                elif operator == '/':
                    constant = 1 / constant
                    operator = '*'
                if operator == '+':
                    val = val + constant
                elif operator == '*':
                    val = val * constant
    finally:
        return val

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

        archive.light_amb_orig += str(reading.get_light_amb_orig()) + '^'
        archive.pres_beer_orig += str(reading.get_pres_beer_orig()) + '^'
        archive.temp_amb_orig += str(reading.get_temp_amb_orig()) + '^'
        archive.temp_beer_orig += str(reading.get_temp_beer_orig()) + '^'

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

def setReadInstant(active_config):
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
    else:
        temp_amb = None
        temp_beer = None

    if bool(temp_amb):
        temp_amb_t = temp_amb.sensor
        temp_amb_d = temp_amb.details
    if bool(temp_beer):
        temp_beer_t = temp_beer.sensor
        temp_beer_d = temp_beer.details

    return [temp_amb_t, temp_amb_d, temp_beer_t, temp_beer_d]

'''Other'''

def getAllData(cur_beer):
    '''Return a DF of reading/archive data, ordered by instant'''
    active_beer = getActiveBeer()
    archive_data = []
    reading_data = []
    archive_key = ''
    reading_key = ''
    
    all_data = [[
            "'Log Time'",
            "'Ambient Temp'", "'Ambient Temp title'", "'Ambient Temp text'",
            "'Beer Temp'", "'Beer Temp title'", "'Beer Temp text'",
            "'Ambient Light'", "'Ambient Light title'", "'Ambient Light text'",
            "'Beer Pressure'", "'Beer Pressure title'", "'Beer Pressure text'"
        ]]
    add = []

    archive_key = getArchiveKey()
    cache_key = cache.get('archive_key')
    if (archive_key == cache_key) and (active_beer == cur_beer):
        archive_data = cache.get('archive_data')
    else:
        archive_key = ''
        active_archives = getAllArchives(cur_beer)
        for archive in active_archives:
            archive_key = archive_key + '^' + archive.get_unique_ident()
            instant_actual_arch = archive.get_instant_actual()
            temp_amb_arch = archive.get_temp_amb()
            temp_beer_arch = archive.get_temp_beer()
            light_amb_arch = archive.get_light_amb()
            pres_beer_arch = archive.get_pres_beer()
            event_temp_amb_arch = archive.get_event_temp_amb()
            event_temp_beer_arch = archive.get_event_temp_beer()
            counter = 0
            while counter < archive.count:
                if bool(event_temp_amb_arch):#Remove this and below when old archives are deleted (missing this field)
                    event_temp_amb = event_temp_amb_arch[counter]
                else:
                    event_temp_amb = None
                if bool(event_temp_beer_arch):
                    event_temp_beer = event_temp_beer_arch[counter]
                else:
                    event_temp_beer = None
                [temp_amb_t, temp_amb_d, temp_beer_t, temp_beer_d] = getEventData(None,event_temp_beer,event_temp_amb)
                if temp_amb_t in ['', None]: temp_amb_t = 'undefined'
                if temp_amb_d in ['', None]: temp_amb_d = 'undefined'
                if temp_beer_t in ['', None]: temp_beer_t = 'undefined'
                if temp_beer_d in ['', None]: temp_beer_d = 'undefined'
                add = [
                        'new Date("' + str(instant_actual_arch[counter]) + '")',
                        temp_amb_arch[counter],temp_amb_t,temp_amb_d,
                        temp_beer_arch[counter],temp_beer_t,temp_beer_d,
                        light_amb_arch[counter],'undefined','undefined',
                        pres_beer_arch[counter],'undefined','undefined'
                    ]
                archive_data.append(data)
                counter += 1
        if active_beer == cur_beer:
            cache.set('archive_key', archive_key)
            cache.set('archive_data', archive_data)
    all_data.extend(archive_data)

    reading_key = getReadingKey()
    cache_key = cache.get('reading_key')
    if (reading_key == cache_key) and (active_beer == cur_beer):
        reading_data = cache.get('reading_data')
    else:
        reading_key = ''
        active_readings = getAllReadings(cur_beer)
        for reading in active_readings:
            reading_key = reading_key + '^' + reading.get_instant_actual()

            [temp_amb_t, temp_amb_d, temp_beer_t, temp_beer_d] = getEventData(reading)
            if temp_amb_t in ['', None]: temp_amb_t = 'undefined'
            if temp_amb_d in ['', None]: temp_amb_d = 'undefined'
            if temp_beer_t in ['', None]: temp_beer_t = 'undefined'
            if temp_beer_d in ['', None]: temp_beer_d = 'undefined'
            add = [
                    'new Date("' + str(reading.get_instant_actual()) + '")',
                    reading.get_temp_amb(),temp_amb_t,temp_amb_d,
                    reading.get_temp_beer(),temp_beer_t,temp_beer_d,
                    reading.get_light_amb(),'undefined','undefined',
                    reading.get_pres_beer(),'undefined','undefined'
                ]
            reading_data.append(add)
        if active_beer == cur_beer:
            cache.set('reading_key', reading_key)
            cache.set('reading_data', reading_data)
    all_data.extend(reading_data)

    return all_data

def get_date_diff(d1,d2, append = "ago"):
    '''Returns the difference between two datetime objects in a readable format'''
    diff = abs(d2-d1)

    if(diff.days > 0): out = str(diff.days) + " day(s)"
    elif(diff.seconds < 60): out = "less than a minute"
    elif(diff.seconds < 60*60): out = str(int(round(diff.seconds/60,0))) + " minute(s)"
    else: out = str(int(round(diff.seconds/(60*60),0))) + " hour(s)"

    if append != None: out = out + " " + append
    return(out)

def get_paint_cols(val, rng = None):
    '''Returns the background color for a value given a set range. In the future, it could also return foreground color'''
    if rng == None or rng == (0,0): bgcol = "#FFFFFF" #White
    elif(rng[0] <= val <= rng[1]): bgcol = "#008000" #Green
    elif(not (rng[0] <= val <= rng[1])): bgcol = "#FF0000" #Red

    fgcol = "#000000" #Black
    return((bgcol, fgcol))

def next_log_estimate():
    '''Estimates the next reading time based on log freq and last logged time'''
    last_reading = getLastReading(getActiveBeer()).instant_actual
    log_freq = None
    for i in range(10):
        r, msg = send2middleware("?code=M")
        print(r)
        if r.upper() == "SUCCESS":
            log_freq = int(msg.split("=")[1])
            break
        sleep(.1)
    out = "unknown amount of time"
    if log_freq != None:
        next = last_reading + timedelta(minutes = log_freq)
        now = nowInUtc()
        if next >= now: out = get_date_diff(now, next, append = None)
        elif next >= now - timedelta(minutes = 5): out = "less than a minute"
    return(out)
    
def getStatus(command):
    sleep(.1)
    s, collection_status = send2middleware(command)
    if s != "Success": out = "?"
    else:
        if "on." in collection_status: out = "on"
        else: out = "off"
    return(out)