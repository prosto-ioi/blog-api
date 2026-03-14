from django.contrib import admin
from django.urls import path, include
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.blog.views import PostViewSet, CommentViewSet, CategoryViewSet, TagViewSet, stats_view
from apps.users.views import UserRegisterViewSet, set_language, set_timezone


class RateLimitedTokenView(TokenObtainPairView):
    @method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')

posts_router = nested_routers.NestedDefaultRouter(router, 'posts', lookup='post')
posts_router.register('comments', CommentViewSet, basename='post-comments')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/register/', UserRegisterViewSet.as_view({'post': 'create'}), name='register'),
    path('api/auth/token/', RateLimitedTokenView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/language/', set_language, name='set_language'),
    path('api/auth/timezone/', set_timezone, name='set_timezone'),

    # Blog
    path('api/', include(router.urls)),
    path('api/', include(posts_router.urls)),

    # Stats
    path('api/stats/', stats_view, name='stats'),

    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]