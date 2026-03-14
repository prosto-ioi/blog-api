import json
import logging
import asyncio
import httpx
import redis as redis_lib

from django.utils import timezone as django_timezone
from django.conf import settings
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from apps.users.models import User
from .models import Category, Comment, Post, Tag
from .serializers import (
    CategorySerializer, CommentSerializer,
    PostSerializer, TagSerializer,
)

logger = logging.getLogger('apps.blog')

POSTS_CACHE_KEY = 'published_posts_list'
POSTS_CACHE_TIMEOUT = 60


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'slug'

    @method_decorator(ratelimit(key='user', rate='20/m', method='POST', block=True))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Post.objects.all()
        return Post.objects.filter(status=Post.Status.PUBLISHED)

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            cache_key = self._get_cache_key(request)
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        response = super().list(request, *args, **kwargs)

        if not request.user.is_authenticated:
            cache.set(self._get_cache_key(request), response.data, POSTS_CACHE_TIMEOUT)
        return response

    def perform_create(self, serializer) -> None:
        serializer.save(author=self.request.user)
        for lang in ['en', 'ru', 'kk']:
            cache.delete(f'published_posts_list_{lang}')
        logger.info('Post created: %s by user %s', serializer.instance.title, self.request.user.email)

    def perform_update(self, serializer) -> None:
        logger.info('Post update attempt: %s by user %s', serializer.instance.slug, self.request.user.email)
        serializer.save()
        for lang in ['en', 'ru', 'kk']:
            cache.delete(f'published_posts_list_{lang}')
        logger.info('Post updated: %s', serializer.instance.title)

    def perform_destroy(self, instance) -> None:
        logger.info('Post deleted: %s by user %s', instance.title, self.request.user.email)
        instance.delete()
        for lang in ['en', 'ru', 'kk']:
            cache.delete(f'published_posts_list_{lang}')


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post__slug=self.kwargs['post_pk'])

    def perform_create(self, serializer) -> None:
        post = Post.objects.get(slug=self.kwargs['post_pk'])
        comment = serializer.save(author=self.request.user, post=post)
        logger.info('Comment created on post %s by user %s', post.title, self.request.user.email)

        try:
            r = redis_lib.from_url(settings.REDIS_URL)
            event = {
                'post_slug': post.slug,
                'author_id': self.request.user.id,
                'author': self.request.user.email,
                'body': comment.body,
            }
            r.publish('comments', json.dumps(event))
            logger.info('Comment event published to Redis channel')
        except Exception:
            logger.exception('Failed to publish comment event to Redis')

    def perform_destroy(self, instance) -> None:
        logger.info('Comment deleted by user %s', self.request.user.email)
        instance.delete()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

@api_view(['GET'])
async def stats_view(request):
    blog_stats = await _get_blog_stats()
    exchange_rates, current_time = await asyncio.gather(
        _fetch_exchange_rates(),
        _fetch_current_time(),
    )
    return Response({
        'blog': blog_stats,
        'exchange_rates': exchange_rates,
        'current_time': current_time,
    })

async def _get_blog_stats() -> dict:
    total_posts = await Post.objects.acount()
    total_comments = await Comment.objects.acount()
    total_users = await User.objects.acount()
    return {
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_users': total_users,
    }

async def _fetch_exchange_rates() -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get('https://open.er-api.com/v6/latest/USD')
            data = response.json()
            rates = data.get('rates', {})
            return {
                'KZT': rates.get('KZT'),
                'RUB': rates.get('RUB'),
                'EUR': rates.get('EUR'),
            }
    except Exception:
        logger.exception('Failed to fetch exchange rates')
        return {}
    
async def _fetch_current_time() -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                'https://timeapi.io/api/time/current/zone?timeZone=Asia/Almaty'
            )
            data = response.json()
            return data.get('dateTime', '')
    except Exception:
        logger.exception('Failed to fetch current time')
        return ''
    
