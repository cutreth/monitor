from monitor.models import Archive

import matplotlib.dates as mpld

def getAllArchives(active_beer):
    all_archives = None
    try:
        all_archives = Archive.objects.filter(beer=active_beer)
    finally:
        return all_archives

def getArchive(active_beer, day):
    active_archive = None    
    try:
        active_archive = Archive.objects.get(beer=active_beer, reading_date=day)
    finally:
        return active_archive

def createArchive(active_beer, day):
    try:
    finally:
    
def updateArchive(archive, reading):
    result = None
    try:
        archive.count += 1
        archive.save()
        reading.delete()
        result = True
    finally:
        return result

