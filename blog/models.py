from django.conf import settings
from django.db import models
from django.utils import timezone

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    views = models.BigIntegerField(default = 0)
    cover = models.ImageField(blank=True, default=None, upload_to='images')
    attachment = models.FileField(blank=True, default=None, upload_to='attachments')
    tags = models.ManyToManyField('blog.Tag', blank=True, default=None)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
    
    def approved_comments(self):
       return self.comments.filter(approved_comment=True)
   
    def likes_count(self):
        return PostLike.objects.filter(post=self).count()

    def dislikes_count(self):
        return PostDislike.objects.filter(post=self).count()
    
    
class Comment(models.Model):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)
   
    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text

class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
class PostLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)

    def __str__ (self):
        return '{} - {}' .format(self.post.title, self.user)

class PostDislike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)

    def __str__ (self):
        return '{} - {}' .format(self.post.title, self.user)

    