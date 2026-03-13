import json
import logging

import redis as redis_lib
from django.conf import settings
from django.core.cache import cache
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

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
            cached = cache.get(POSTS_CACHE_KEY)
            if cached is not None:
                return Response(cached)

        response = super().list(request, *args, **kwargs)

        if not request.user.is_authenticated:
            cache.set(POSTS_CACHE_KEY, response.data, POSTS_CACHE_TIMEOUT)
        return response

    def perform_create(self, serializer) -> None:
        serializer.save(author=self.request.user)
        cache.delete(POSTS_CACHE_KEY)
        logger.info('Post created: %s by user %s', serializer.instance.title, self.request.user.email)

    def perform_update(self, serializer) -> None:
        logger.info('Post update attempt: %s by user %s', serializer.instance.slug, self.request.user.email)
        serializer.save()
        cache.delete(POSTS_CACHE_KEY)
        logger.info('Post updated: %s', serializer.instance.title)

    def perform_destroy(self, instance) -> None:
        logger.info('Post deleted: %s by user %s', instance.title, self.request.user.email)
        instance.delete()
        cache.delete(POSTS_CACHE_KEY)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        # nested router передаёт post_pk (значение lookup поля — slug)
        return Comment.objects.filter(post__slug=self.kwargs['post_pk'])

    def perform_create(self, serializer) -> None:
        post = Post.objects.get(slug=self.kwargs['post_pk'])
        comment = serializer.save(author=self.request.user, post=post)
        logger.info('Comment created on post %s by user %s', post.title, self.request.user.email)

        try:
            r = redis_lib.from_url(settings.REDIS_URL)
            event = {
                'post_slug': post.slug,
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