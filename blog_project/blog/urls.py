from django.urls import path

from . import views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    LikeRedirectView,
    FriendListView,
    FriendRequestListView,
    AddFriendListView,
    AddFriendRedirectView,
    ProcessRequestRedirectView,
    PostShareListView,
    PostShareRedirectView,
    FriendDeleteRedirectView, SharedPostsListView, PostShareDeleteRedirectView
)

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('like/', LikeRedirectView.as_view(), name='like'),
    path('friends/', FriendListView.as_view(), name='friends'),
    path('friend-request/', FriendRequestListView.as_view(), name='friend-request'),
    path('add-friend/', AddFriendListView.as_view(), name='add-friend'),
    path('added-friend/', AddFriendRedirectView.as_view(), name='added-friend'),
    path('process-request/', ProcessRequestRedirectView.as_view(), name='process-request'),
    path('post/<int:pk>/share/', PostShareListView.as_view(), name='post-share'),
    path('post-shared/', PostShareRedirectView.as_view(), name='post-shared'),
    path('deleted-friend/', FriendDeleteRedirectView.as_view(), name='deleted-friend'),
    path('shared-posts/', SharedPostsListView.as_view(), name='shared-posts'),
    path('delete-shared-post/', PostShareDeleteRedirectView.as_view(), name='delete-shared-post'),

]
