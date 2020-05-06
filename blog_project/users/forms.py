from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from .models import Profile
from .Classifier.chose_file import classify_file
import tempfile
import os
from django.core.files.storage import default_storage
from django.conf import settings


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    def is_valid(self):
        super().is_valid()
        image = self.cleaned_data.get('image')
        path = default_storage.save(settings.MEDIA_ROOT + '\\raccoon.jpg', ContentFile(image.read()))
        raccoon_likeliness = classify_file(path)
        os.remove(path)

        if raccoon_likeliness < 0.9:
            return False
        return True

    class Meta:
        model = Profile
        fields = ['image']