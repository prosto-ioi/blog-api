import redis
import json
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Listen to Redis channel "comments" and print messages'

    def handle(self, *args, **options):
        self.stdout.write('Starting comment listener...')
        r = redis.Redis.from_url(settings.REDIS_URL)
        pubsub = r.pubsub()
        pubsub.subscribe('comments')

        self.stdout.write('Subscribed to channel "comments". Waiting for messages...')
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    self.stdout.write(self.style.SUCCESS(f'New comment: {data}'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Error: {e}'))