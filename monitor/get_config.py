from monitor.models import Config
from monitor.get_reading import genReadingKey
from monitor.get_archive import genArchiveKey
import datetime

def getActiveConfig():
    active_config = Config.objects.filter()[:1].get()
    return active_config

def getActiveBeer():
    active_config = getActiveConfig()
    active_beer = active_config.beer
    return active_beer

def SetReadInstant(active_config):
    '''Set the current instant as active_config.read_last_instant'''
    right_now = datetime.datetime.now()
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
    reading_key = genReadingKey()
    setReadingKey(reading_key)
    return None
    
def updateArchiveKey():
    archive_key = genArchiveKey()
    setArchiveKey(archive_key)
    return None        
