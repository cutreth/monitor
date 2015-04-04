from django.core.management.base import BaseCommand

from monitor.do import updateReadingKey, updateArchiveKey

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
            
        updateArchiveKey()
        updateReadingKey()

        return None
