import logging
import redis
import json
from django.conf import settings
from rest_framework import viewsets, permissions, status
from django.core.cache import cache
from rest_framework.response import Response
from .models import Post, Comment, Category, Tag
from .serializers import PostSerializer, CommentSerializer, CategorySerializer, TagSerializer
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        # Только опубликованные посты для неавторизованных
        if self.request.user.is_authenticated:
            return Post.objects.all()
        return Post.objects.filter(status=Post.Status.PUBLISHED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        logger.info('Post created: %s by user %s', serializer.instance.title, self.request.user.email)

    def perform_update(self, serializer):
        logger.info('Post update attempt: %s by user %s', serializer.instance.title, self.request.user.email)
        serializer.save()
        logger.info('Post updated: %s', serializer.instance.title)

    def perform_destroy(self, instance):
        logger.info('Post deleted: %s by user %s', instance.title, self.request.user.email)
        instance.delete()

    def list(self, request, *args, **kwargs):
        cache_key = 'published_posts_list'
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            # Если данные есть в кэше, возвращаем их
            return Response(cached_data)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        cache.set(cache_key, data, timeout=60)
        return Response(data)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        cache.delete('published_posts_list')
        logger.info('Post created: %s by user %s', serializer.instance.title, self.request.user.email)

    def perform_update(self, serializer):
        logger.info('Post update attempt: %s by user %s', serializer.instance.title, self.request.user.email)
        serializer.save()
        cache.delete('published_posts_list')
        logger.info('Post updated: %s', serializer.instance.title)

    def perform_destroy(self, instance):
        logger.info('Post deleted: %s by user %s', instance.title, self.request.user.email)
        instance.delete()
        cache.delete('published_posts_list')

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post__slug=self.kwargs["post_slug"])
    
    def perform_create(self, serializer):
        post = Post.objects.get(slug=self.kwargs["post_slug"])
        serializer.save(author=self.request.user, post=post)
        logger.info('Comment created on post %s by user %s', post.title, self.request.user.email)

    def perform_update(self, serializer):
        logger.info('Comment update attempt by user %s', self.request.user.email)
        serializer.save()
        logger.info('Comment updated')

    def perform_destroy(self, instance):
        logger.info('Comment deleted by user %s', self.request.user.email)
        instance.delete()

    def perform_create(self, serializer):
        post = Post.objects.get(slug=self.kwargs["post_slug"])
        comment = serializer.save(author=self.request.user, post=post)

        # Публикация в Redis
        try:
            redis_conn = get_redis_connection("default")
            message = {
                'id': comment.id,
                'post_slug': post.slug,
                'author_email': comment.author.email,
                'body': comment.body,
                'created_at': str(comment.created_at)
            }
            redis_conn.publish('comments', json.dumps(message))
            logger.info('Published comment event to Redis channel "comments"')
        except Exception as e:
            logger.exception('Failed to publish comment event to Redis: %s', e)

        logger.info('Comment created on post %s by user %s', post.title, self.request.user.email)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

