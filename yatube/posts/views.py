from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    context = {'page_obj': paginator(request, post_list,
                                     settings.POSTS_PER_PAGE), }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {'group': group,
               'page_obj': paginator(request, post_list,
                                     settings.POSTS_PER_PAGE)}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    author_posts_count = author_posts.count()
    if request.user.is_authenticated is True:
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
        else:
            following = False
    else:
        following = False
    if author == request.user:
        is_self_author = True
    else:
        is_self_author = False
    context = {'page_obj': paginator(request, author_posts,
                                     settings.POSTS_PER_PAGE),
               'author': author,
               'author_posts_count': author_posts_count,
               'is_profile': True,
               'following': following,
               'is_self_author': is_self_author}
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = get_object_or_404(User, username=post.author)
    author_posts_count = author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {'post': post, 'author_posts_count': author_posts_count,
               'form': form, 'comments': comments}
    if request.user == post.author:
        context = {'post': post, 'author_posts_count': author_posts_count,
                   'form': form, 'comments': comments, 'is_edit': True}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
    context = {'form': form}
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    else:
        if request.method == "POST":
            form = PostForm(request.POST,
                            files=request.FILES or None,
                            instance=post)
            if form.is_valid():
                post.save()
                return redirect('posts:post_detail', post_id)
        form = PostForm(instance=post)
        context = {'form': form, 'is_edit': True}
        return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    authors = Follow.objects.filter(user=request.user).values_list('author')
    post_list = Post.objects.filter(author__in=authors)
    if post_list.count() > 0:
        is_following = True
    else:
        is_following = False
    context = {'page_obj': paginator(request, post_list,
                                     settings.POSTS_PER_PAGE),
               'is_following': is_following}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        if Follow.objects.filter(user=request.user,
                                 author=author).exists() is False:
            Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        if Follow.objects.filter(user=request.user,
                                 author=author).exists() is True:
            Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
