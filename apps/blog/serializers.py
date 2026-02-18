from rest_framework import serializers
from .models import Post, Comment, Category, Tag

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["author", "post"]

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    cauthor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ["author", "created_at", "updated_at"]
