from django.contrib import admin

from .models import Post, Like, Friend, SharedPost, FriendRequest, Comment

admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Friend)
admin.site.register(SharedPost)
admin.site.register(FriendRequest)
admin.site.register(Comment)
