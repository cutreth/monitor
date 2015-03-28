from django.core.management.base import BaseCommand
from monitor.models import Reading, Archive
from monitor.views import getActiveBeer

import matplotlib.dates as mpld
import datetime

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        #Define a datetime one week ago
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=6)
        
        #Return readings for active_beer before the date limit
        active_beer = getActiveBeer()
        active_readings = Reading.objects.filter(beer=active_beer).filter(instant_actual__lte=week_ago)
        
        for day in active_readings.dates('instant_actual','day',order='DESC'):
            new_archive = Archive(beer = active_beer, reading_date = day)
            day_readings = active_readings.filter(instant_actual__gte=day)
            for reading in day_readings:
                new_archive.instant_actual = str(mpld.date2num(reading.instant_actual)) + '^'
                new_archive.light_amb = str(reading.light_amb) + '^'
                new_archive.pres_beer = str(reading.pres_beer) + '^'
                new_archive.temp_amb = str(reading.temp_amb) + '^'
                new_archive.temp_beer = str(reading.temp_beer) + '^'
                new_archive.count += 1
                new_archive.save()
                reading.delete()

        return None

'''

http://stackoverflow.com/questions/20847791/pandas-dataframe-as-field-in-django

'''