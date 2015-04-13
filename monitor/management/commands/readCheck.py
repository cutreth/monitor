from django.core.management.base import BaseCommand

import monitor.api as api
import monitor.do as do

import datetime

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        active_config = do.getActiveConfig()
        active_beer = do.getActiveBeer()
        read_missing = active_config.read_missing
        read_last_instant = active_config.read_last_instant
        time_delta = datetime.timedelta(minutes=read_missing)

        read_expected = api.MissingErrorCheck(read_missing,read_last_instant,time_delta)

        if read_expected:
            error_details = 'No reading since: ' + str(read_last_instant)
            do.createEvent(active_beer, None, 'Missing', None, error_details)
            message = api.BuildErrorEmail(active_config, None, error_details)
            api.SendErrorEmail(active_config, message)

        return None
