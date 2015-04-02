from django.core.management.base import BaseCommand

from monitor.get_config import getActiveBeer, getActiveConfig
from monitor.get_reading import getAllReadings
from monitor.get_archive import getAllArchives

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        
        active_config = getActiveConfig()
        active_beer = getActiveBeer()

        archive_key = ''
        active_archives = getAllArchives(active_beer)
        for archive in active_archives:
            archive_key = archive_key + '^' + archive.get_unique_ident()

        reading_key = ''
        active_readings = getAllReadings(active_beer) 
        for reading in active_readings:
            reading_key = reading_key + '^' + reading.get_instant_actual()
            
        active_config.archive_key = archive_key
        active_config.reading_key = reading_key
        active_config.save()

        return None
