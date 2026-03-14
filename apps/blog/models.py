from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)
    name_ru = models.CharField(max_length=100, default='', blank=True)
    name_kk = models.CharField(max_length=100, default='', blank=True)
    slug = models.SlugField(unique=True) 

    def __str__(self):
        return self.name
    
    def get_namme(self, lang: str = 'en'):
        if lang == 'ru' and self.name_ru:
            return self.name_ru
        if lang == 'kk' and self.name_kk:
            return self.name_kk
        return self.name
    
    
class Tag(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField(_('body'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(_('body'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
