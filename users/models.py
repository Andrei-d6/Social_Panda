import os

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # taking the image form the instance
        img = Image.open(self.image.path)

        if self.image.name != 'default.jpg':
            old_image_path = settings.MEDIA_ROOT + 'profile_pics' + self.user.profile.image.name
            # if os.path.isfile(old_image_path) and self.form.is_valid():
            #     os.remove(old_image_path)

        if img.height > 300 or img.width < 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
