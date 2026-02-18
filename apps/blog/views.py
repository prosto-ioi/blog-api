import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Post, Comment, Category, Tag
from .serializers import PostSerializer, CommentSerializer, CategorySerializer, TagSerializer

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
        
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

