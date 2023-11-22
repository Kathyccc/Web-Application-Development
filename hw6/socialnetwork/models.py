from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Post(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    creation_time = models.DateTimeField()

    def __str__(self):
        return f'id={self.id}, text="{self.text}"'
    
class Profile(models.Model):
    bio = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    following = models.ManyToManyField(User, related_name="followers", blank=True)

class Comment(models.Model):
    text = models.CharField(max_length=200)  
    creator = models.ForeignKey(User, on_delete=models.PROTECT)  
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)  
    creation_time = models.DateTimeField()

    def __str__(self):
        return f'Comment {self.id} on Post {self.post.id} by {self.user.username}'


