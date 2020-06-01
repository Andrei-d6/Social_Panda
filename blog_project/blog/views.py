
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import resolve, Resolver404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    RedirectView,
)

from .models import Post, Like, Friend, FriendRequest, SharedPost, Comment


def home(request):
    context = {"posts": Post.objects.all()}
    return render(request, "blog/home.html", context)


class PostListView(ListView):
    # we need to create a variable named model
    model = Post
    template_name = "blog/home.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = 3  # this adds first pagination functionality

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return (
                Post.objects.all().annotate(
                    like_count=Count("likes", distinct=True),
                    comments_count=Count("comment", distinct=True),
                    liked=Count("likes", filter=Q(likes__user=self.request.user), distinct=True)
                ).order_by("-date_posted")
            )
        else:
            return Post.objects.all().annotate(like_count=Count("likes")).order_by("-date_posted")


class UserPostListView(ListView):
    # we need to create a variable named model
    model = Post
    template_name = "blog/user_posts.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"
    paginate_by = 3  # this adds first pagination functionality

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by("-date_posted")


class PostDetailView(DetailView):
    # for this view we will use the default template name
    # so we don't need to specify it here
    model = Post

    def get_context_data(self, **kwargs):
        comments = Comment.objects.filter(post_id=self.object.id).order_by(
            "-date_of_comment"
        )
        likes_count = Like.objects.filter(post_id=self.object.id).count()
        kwargs.update({"comments": comments,
                       "likes_count": likes_count,
                       "comments_count": len(comments)
                       })
        return super().get_context_data(object_list=None, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    # for this view we will use the default template name
    # so we don't need to specify it here
    model = Post
    fields = ["title", "content", "image"]

    def form_invalid(self, form):
        if not form.instance.content and not form.instance.image:
            return JsonResponse(form.errors, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # for this view we will use the default template name
    # so we don't need to specify it here
    model = Post
    fields = ["title", "content", "image"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    # default template_name post_confirm_delete.html
    model = Post
    success_url = "/"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, "blog/about.html", {"title": "About"})


class LikeRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            user = self.request.user
            post = self.request.POST["post_id"]
            current_page = self.request.POST["current_page"]

            post_author = Post.objects.get(pk=post).author
            liked = Like.objects.filter(
                user=user, post=Post.objects.get(pk=post)
            ).exists()

            if user != post_author and not liked:
                Like.objects.create(user=user, post=Post.objects.get(pk=post))
            elif user != post_author:
                Like.objects.filter(user=user, post=Post.objects.get(pk=post)).delete()

            return current_page
        else:
            return super().get_redirect_url(*args, **kwargs)


class FriendListView(LoginRequiredMixin, ListView):
    model = Friend
    template_name = "blog/friend_list.html"
    context_object_name = "friends"
    paginate_by = 3

    def get_queryset(self):
        return Friend.objects.filter(current_user_id=self.request.user.id)


class FriendRequestListView(LoginRequiredMixin, ListView):
    model = Friend
    template_name = "blog/friend_request.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        friend_requests = FriendRequest.objects.filter(receiver_id=self.request.user.id)
        kwargs.update({"friend_requests": friend_requests})
        return super().get_context_data(object_list=None, **kwargs)


class AddFriendListView(LoginRequiredMixin, ListView):
    model = Friend
    template_name = "blog/add_friend.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        username = self.request.GET.get("username", "")
        users = User.objects.filter(username__icontains=username)
        current_user = self.request.user

        if not username:
            users = User.objects.none()

        new_users = []
        for user in users:
            if (
                    not Friend.objects.filter(current_user_id=current_user.id).filter(
                        current_user_friend_id=user.id
                    )
                    and user.id != current_user.id
            ):
                if FriendRequest.objects.filter(receiver_id=user.id).filter(
                        sender_id=current_user.id
                ):
                    new_users.append((user, False))
                else:
                    new_users.append((user, True))

        kwargs.update({"users": new_users})
        return super().get_context_data(object_list=None, **kwargs)


class AddFriendRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            current_user = self.request.user
            current_page = self.request.POST["current_page"]
            friend = int(self.request.POST["friend"])

            friend = User.objects.get(id=friend)
            FriendRequest.objects.create(sender=current_user, receiver=friend)
            return current_page
        else:
            return super().get_redirect_url(*args, **kwargs)


class ProcessRequestRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            current_user = self.request.user
            accepted = self.request.GET["accepted"]
            friend = int(self.request.GET["friend"])
            friend = User.objects.get(id=friend)

            if str(accepted) == "true":
                Friend.objects.create(
                    current_user=current_user, current_user_friend=friend
                )
                Friend.objects.create(
                    current_user=friend, current_user_friend=current_user
                )

            if FriendRequest.objects.filter(
                    sender_id=friend.id, receiver_id=current_user.id
            ).exists():
                FriendRequest.objects.get(
                    sender_id=friend.id, receiver_id=current_user.id
                ).delete()

            if FriendRequest.objects.filter(
                    receiver_id=friend.id, sender_id=current_user.id
            ).exists():
                FriendRequest.objects.get(
                    receiver_id=friend.id, sender_id=current_user.id
                ).delete()

            return "/friend-request/"
        else:
            return super().get_redirect_url(*args, **kwargs)


class PostShareListView(LoginRequiredMixin, ListView):
    model = Friend
    template_name = "blog/share.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        friends = Friend.objects.filter(current_user_id=self.request.user.id)
        post_id = self.kwargs["pk"]
        current_user = self.request.user

        friends_shared = []
        for friend in friends:
            if (
                    SharedPost.objects.filter(post_id=post_id)
                            .filter(post_sender=current_user)
                            .filter(post_receiver=friend.current_user_friend)
                            .exists()
            ):
                shared = True
            else:
                shared = False
            friends_shared.append((friend, shared))

        kwargs.update(
            {"friends_shared": friends_shared, "post_id": post_id, }
        )
        return super().get_context_data(object_list=None, **kwargs)


class PostShareRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            current_user = self.request.POST["current_user"]
            current_user_friend = self.request.POST["current_user_friend"]
            current_user = User.objects.get(username=current_user)
            current_user_friend = User.objects.get(username=current_user_friend)

            post_id = int(self.request.POST["post_id"])
            current_page = self.request.POST["current_page"]

            post = Post.objects.get(id=post_id)
            SharedPost.objects.create(
                post_sender=current_user, post_receiver=current_user_friend, post=post
            )
            return current_page
        else:
            return super().get_redirect_url(*args, **kwargs)


class FriendDeleteRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            friend_to_delete_id = int(self.request.GET["friend_to_delete"])
            current_user_id = self.request.user.id
            current_page = self.request.GET["current_page"]

            if Friend.objects.filter(current_user_id=current_user_id,
                                     current_user_friend_id=friend_to_delete_id).exists():
                Friend.objects.get(
                    current_user_id=current_user_id,
                    current_user_friend_id=friend_to_delete_id,
                ).delete()

            if Friend.objects.filter(current_user_id=friend_to_delete_id,
                                     current_user_friend_id=current_user_id).exists():
                Friend.objects.get(
                    current_user_id=friend_to_delete_id,
                    current_user_friend_id=current_user_id,
                ).delete()

            try:
                resolve(current_page)
            except Resolver404:
                page_index = int(current_page[-1])
                page_index -= 1

                if page_index >= 1:
                    current_page = current_page[:-1]
                    current_page += str(page_index)
                else:
                    current_page = '/friends/'

            return current_page
        else:
            return super().get_redirect_url(*args, **kwargs)


class SharedPostsListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/shared_posts.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = 3  # this adds first pagination functionality

    def get_queryset(self):
        shared_posts = SharedPost.objects.filter(post_receiver_id=self.request.user.id)
        posts = []

        for post in shared_posts:
            posts.append((post.post, post.post_sender.username))

        return posts


class PostShareDeleteRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            current_user = self.request.user
            post_id = int(self.request.POST["post_id"])
            current_page = self.request.POST["current_page"]
            sender = self.request.POST["sender_name"]
            sender = User.objects.get(username=sender)

            if Post.objects.filter(id=post_id).exists():
                post = Post.objects.get(id=post_id)

                if SharedPost.objects.filter(
                        post_sender_id=sender.id,
                        post_receiver_id=current_user.id,
                        post_id=post.id,
                ).exists():

                    SharedPost.objects.get(
                        post_sender_id=sender.id,
                        post_receiver_id=current_user.id,
                        post_id=post.id,
                    ).delete()
                else:
                    print(f'sender: {sender.username}\nreceiver: {current_user.username}')

            try:
                resolve(current_page)
            except Resolver404:
                page_index = int(current_page[-1])
                page_index -= 1

                if page_index >= 1:
                    current_page = current_page[:-1]
                    current_page += str(page_index)
                else:
                    current_page = '/shared-posts/'
            return current_page
        else:
            return super().get_redirect_url(*args, **kwargs)


class AddCommentRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            current_user = self.request.user
            current_page = self.request.POST["current_page"]
            post_id = int(self.request.POST["post_id"])
            text = self.request.POST["text"]

            post = Post.objects.get(id=post_id)
            Comment.objects.create(user=current_user, post=post, text=text)
            return current_page
        else:
            return super().get_redirect_url(*args, **kwargs)


class SearchListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/search.html"
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = 2

    def get_queryset(self):
        searched_word = self.request.GET.get("search_for", "")
        self.kwargs.update({"search_for": searched_word})
        if searched_word == '':
            return Post.objects.none()

        posts = Post.objects.filter(
            Q(title__icontains=searched_word) |
            Q(author__username__icontains=searched_word) |
            Q(content__icontains=searched_word)
        ).annotate(
            like_count=Count("likes", distinct=True),
            liked=Count("likes", filter=Q(likes__user=self.request.user), distinct=True),
            comments_count=Count("comment", distinct=True)).order_by("-date_posted")

        if not posts:
            messages.warning(
                self.request, f"Nothing to be found for your search!"
            )
            return Post.objects.none()

        # self.kwargs.update({"search_for": searched_word})
        return posts

