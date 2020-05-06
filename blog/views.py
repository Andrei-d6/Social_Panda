from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView, RedirectView)
from .models import Post, Like


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    # we need to create a variable named model
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5  # this adds first pagination functionality

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Post.objects.all().annotate(like_count=Count('likes'),
                                               liked=Count('likes', filter=Q(likes__user=self.request.user))
                                               ).order_by('-date_posted')
        else:
            return Post.objects.all().annotate(like_count=Count('likes'))


class UserPostListView(ListView):
    # we need to create a variable named model
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5  # this adds first pagination functionality

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    # for this view we will use the default template name
    # so we don't need to specify it here
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    # for this view we will use the default template name
    # so we don't need to specify it here
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # for this view we will use the default template name
    # so we don't need to specify it here
    model = Post
    fields = ['title', 'content']

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
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


class LikeRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            user = self.request.user
            post = self.request.POST['post_id']
            current_page = self.request.POST['current_page']

            post_author = Post.objects.get(pk=post).author
            liked = Like.objects.filter(user=user, post=Post.objects.get(pk=post)).exists()

            if user != post_author and not liked:
                Like.objects.create(user=user, post=Post.objects.get(pk=post))
            elif user != post_author:
                Like.objects.filter(user=user, post=Post.objects.get(pk=post)).delete()

            return current_page
        else:
            return super().get_redirect_url(*args, **kwargs)
