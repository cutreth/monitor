from django.core.management.base import BaseCommand

from monitor.do import do

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
            
        do.updateArchiveKey()
        do.updateReadingKey()

        return None
