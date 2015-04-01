from monitor.models import Config
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
