from django.core.management.base import BaseCommand

from monitor.middleware import sendCommand

from datetime import datetime

class Command(BaseCommand):
    args = None
    help = 'Syncs the server\'s time with Django\'s time'

    def handle(self, *args, **options):
        time = datetime.utcnow().timestamp()
        command = "?code=s&time=" + str(time)
        s,msg = sendCommand(command)
        return(s)