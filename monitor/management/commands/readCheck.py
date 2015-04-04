from django.core.management.base import BaseCommand
from monitor.models import Config
from monitor.views import SendErrorEmail, BuildErrorEmail, isTimeBefore
from monitor.do import nowInUtc

import datetime

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        read_expected = True #Assume need a reading
        active_config = Config.objects.filter()[:1].get()
        read_missing = active_config.read_missing
        read_last_instant = active_config.read_last_instant
        right_now = nowInUtc()
        time_delta = datetime.timedelta(minutes=read_missing)

        if read_missing > 0:
            if bool(read_last_instant):
                if not isTimeBefore(read_last_instant, right_now, time_delta):
                    read_expected = False
        else:
            read_expected = False

        if read_expected:
            error_details = 'No reading since: ' + str(read_last_instant)
            message = BuildErrorEmail(active_config, None, error_details)
            SendErrorEmail(active_config, message)

        return None
