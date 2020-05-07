from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()  # unrestriced text
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')


class Friend(models.Model):
    current_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='current_user')
    current_user_friend = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                            related_name='current_user_friend')


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')


class SharedPost(models.Model):
    post_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_sender')
    post_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_receiver')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
