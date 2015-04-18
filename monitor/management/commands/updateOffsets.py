from django.core.management.base import BaseCommand

import monitor.do as do

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
            
        #do.updateArchiveOffsets()
        do.updateReadingOffsets()
        #Update events

        return None
