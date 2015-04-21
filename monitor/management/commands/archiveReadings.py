from django.core.management.base import BaseCommand

import monitor.do as do

import datetime

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        today = do.nowInUtc().date()
        week_ago = today - datetime.timedelta(days=6)
        #Normally set days=6 for one week

        all_beer = do.getAllBeer()

        for beer in all_beer:
            active_readings = None
            archive = None
            day_readings = None
            active_readings = do.getAllReadings(beer)
            if bool(active_readings):
                active_readings = active_readings.filter(instant_actual__lte=week_ago)
                for day in active_readings.datetimes('instant_actual', 'day', order='DESC'):
                    archive = do.getArchive(beer, day)
                    if not bool (archive):
                        archive = do.createArchive(beer, day)
                    day_readings = active_readings.filter(instant_actual__gte=day)
                    for reading in day_readings:
                        do.updateArchive(archive, reading)

        do.updateArchiveKey()
        do.updateReadingKey()
        return None

'''
http://stackoverflow.com/questions/20847791/pandas-dataframe-as-field-in-django
'''