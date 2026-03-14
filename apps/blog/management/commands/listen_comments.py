import asyncio
import json
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('apps.blog')

COMMENTS_CHANNEL = 'comments'


class Command(BaseCommand):
    help = 'Subscribe to Redis comments channel (async)'

    def handle(self, *args, **kwargs) -> None:
        asyncio.run(self._listen())

    async def _listen(self) -> None:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        pubsub = r.pubsub()
        await pubsub.subscribe(COMMENTS_CHANNEL)
        self.stdout.write(f'Listening on Redis channel: {COMMENTS_CHANNEL}')
        logger.info('Started async listening on Redis channel: %s', COMMENTS_CHANNEL)

        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    self.stdout.write(
                        f"New comment on '{data['post_slug']}' "
                        f"by author_id={data['author_id']}: {data['body']}"
                    )
                    logger.info('Received comment event: %s', data)
                except Exception:
                    logger.exception('Failed to parse comment event')