"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.blog.views import PostViewSet, CommentViewSet, CategoryViewSet, TagViewSet
from apps.users.views import UserRegisterViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from apps.users.views import UserRegisterViewSet
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

class PostViewSet(viewsets.ModelViewSet):
    @method_decorator(ratelimit(key='user', rate='20/m', method='POST'))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("categories", CategoryViewSet)
router.register("tags", TagViewSet)


urlpatterns = [
    path("api/auth/register/", UserRegisterViewSet.as_view({"post": "create"}), name = "register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path('api/auth/register/', register_view, name='register'),
]
