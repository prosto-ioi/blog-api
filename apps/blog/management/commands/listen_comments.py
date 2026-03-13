import json
import logging

import redis
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger('apps.blog')

COMMENTS_CHANNEL = 'comments'


class Command(BaseCommand):
    help = 'Subscribe to Redis comments channel and print incoming events'

    def handle(self, *args, **kwargs) -> None:
        r = redis.from_url(settings.REDIS_URL)
        pubsub = r.pubsub()
        pubsub.subscribe(COMMENTS_CHANNEL)
        self.stdout.write(f'Listening on Redis channel: {COMMENTS_CHANNEL}')
        logger.info('Started listening on Redis channel: %s', COMMENTS_CHANNEL)

        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    self.stdout.write(
                        f"New comment on '{data['post_slug']}' "
                        f"by {data['author']}: {data['body']}"
                    )
                    logger.info('Received comment event: %s', data)
                except Exception:
                    logger.exception('Failed to parse comment event')
