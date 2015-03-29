from django.core.management.base import BaseCommand
from monitor.models import Archive
from monitor.views import getActiveBeer, getReadings
from monitor.archive import getArchive, createArchive, updateArchive

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
        active_readings = getReadings(active_beer)
        active_readings = active_readings.filter(instant_actual__lte=week_ago)

        for day in active_readings.dates('instant_actual', 'day', order='DESC'):
            archive = getArchive(active_beer, day)
            if not bool (archive):
                archive = createArchive(active_beer, day)
            day_readings = active_readings.filter(instant_actual__gte=day)
            for reading in day_readings:
                updateArchive(archive, reading)

        return None

'''
http://stackoverflow.com/questions/20847791/pandas-dataframe-as-field-in-django
'''