from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


def paginator_func(posts, request):
    paginator = Paginator(posts, settings.NUM_POSTS_PER_PAGE)
    print('REQUEST IN PAGINATOR', request)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def index(request):
    posts = Post.objects.all()
    page_obj = paginator_func(posts, request)
    context = {"page_obj": page_obj}
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.post.all()
    page_obj = paginator_func(posts, request)
    context = {"page_obj": page_obj, "group": group}
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    page_obj = paginator_func(author_posts, request)
    context = {"page_obj": page_obj, "author": author}
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = post.author
    count = Post.objects.filter(author_id=user).all().count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'count': count,
        'comments': comments,
        'form': form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,  files=request.FILES or None,)
    context = {
        'form': form,
        'is_edit': False,
    }
    if not form.is_valid():
        return render(request, "posts/create_post.html", context)

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", username=request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if not form.is_valid():
        context = {"form": form, "post_id": post_id, "is_edit": True}
        return render(request, "posts/create_post.html", context)
    form.save()
    return redirect("posts:post_detail", post_id=post_id)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post.id)
    return render(
        request,
        'posts/post_detail.html',
        {
            'form': form,
            'post': post
        }
    )

@login_required
def follow_index(request):
    print('follw_index request')
    post_list = Post.objects.filter(author__following__user=request.user).all()
    context = {'page_obj': paginator_func(post_list, request)}
    return render(request, 'posts/index.html', context)



@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
