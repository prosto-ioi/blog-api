from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.blog.views import PostViewSet, CommentViewSet, CategoryViewSet, TagViewSet
from apps.users.views import UserRegisterViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')

posts_router = nested_routers.NestedDefaultRouter(router, 'posts', lookup='post')
posts_router.register('comments', CommentViewSet, basename='post-comments')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', UserRegisterViewSet.as_view({'post': 'create'}), name='register'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/', include(posts_router.urls)),
]