import pytz
from django.utils import timezone
from django.utils.formats import date_format
from rest_framework import serializers
from rest_framework.request import Request

from .models import Post, Comment, Category, Tag

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_name(self, obj) -> str:
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'en') if request else 'en'
        return obj.get_name(lang)
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["author", "post", "created_at"]

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ["author", "created_at", "updated_at"]

    def _format_date(self, dt) -> str:
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.timezone:
            try:
                tz = pytz.timezone(request.user.timezone)
                dt = dt.astimezone(tz)
            except Exception:
                pass
        return date_format(dt, format='DATETIME_FORMAT', use_l10n=True)
    
    def get_created_at(self, obj) -> str:
        return self._format_date(obj.created_at)
    
    def get_updated_at(self, obj) -> str:
        return self._format_date(obj.updated_at)