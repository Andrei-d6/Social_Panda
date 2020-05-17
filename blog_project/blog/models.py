from PIL import Image
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)  # unrestriced text
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to="post_pics")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # taking the image form the instance
        try:
            img = Image.open(self.image.path)
        except ValueError:
            return

        if img.height > 1000 or img.width > 1000:
            output_size = (1000, 1000)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f'{self.user.username}  {self.post.title}'


class Friend(models.Model):
    current_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="current_user"
    )
    current_user_friend = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="current_user_friend"
    )

    def __str__(self):
        return f'{self.current_user.username} - {self.current_user_friend.username}'


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver"
    )

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}'


class SharedPost(models.Model):
    post_sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_sender"
    )
    post_receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_receiver"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post_sender.username} {self.post.title} {self.post_receiver.username}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment')
    date_of_comment = models.DateTimeField(default=timezone.now)
    text = models.TextField()

    def __str__(self):
        return self.user.username + " " + self.post.title
