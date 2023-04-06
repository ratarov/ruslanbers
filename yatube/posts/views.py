from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from taggit.models import Tag

from .utils import get_posts_context, get_authors_context
from .forms import CommentForm, PostForm
from .models import Comment, Group, Follow, Like, Post, User


@cache_page(settings.INDEX_CACHE_TIMEOUT, key_prefix="index_page")
def index(request, tag_slug=None):
    posts = Post.objects.select_related('group', 'author')
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    context = get_posts_context(posts, request)
    context['tag'] = tag
    context['tags_colors'] = settings.TAGS_COLORS
    return render(request, 'posts/index.html', context)


def search(request):
    search = request.GET.get('q')
    context = get_posts_context(
        Post.objects.select_related('group', 'author').filter(
            text__icontains=search
        ),
        request
    )
    context['tags_colors'] = settings.TAGS_COLORS
    return render(request, 'posts/index.html', context)


@login_required
def follow_index(request):
    context = get_posts_context(
        Post.objects.filter(
            author__following__user=request.user
        ).select_related('group'),
        request
    )
    context['tags_colors'] = settings.TAGS_COLORS
    return render(request, 'posts/follow.html', context)


def groups(request):
    groups = Group.objects.all()
    return render(request, 'posts/groups_all.html', {"page_obj": groups})


def authors_list(request):
    authors = User.objects.annotate(posts_qty=Count('posts')).order_by(
        '-posts_qty'
    ).exclude(username__in=('admin', 'superadmin'))
    context = get_authors_context(authors, request)
    context['posts_king'] = authors[0]
    context['comments_king'] = User.objects.annotate(
        comments_qty=Count('comments')).order_by('-comments_qty')[0]
    context['tags_colors'] = settings.TAGS_COLORS
    return render(request, 'posts/authors_list.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
    }
    context.update(
        get_posts_context(
            group.posts.select_related('author'),
            request
        )
    )
    context['tags_colors'] = settings.TAGS_COLORS
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    context = {
        'author': author,
    }
    context.update(
        get_posts_context(author.posts.select_related('group'), request)
    )
    if request.user.is_authenticated:
        context['following'] = request.user.follower.filter(
            author=author).exists()
    context['tags_colors'] = settings.TAGS_COLORS
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        id=post_id
    )
    comments = post.comments.all()
    form = CommentForm()
    liked = (request.user.is_authenticated
             and request.user.liker.filter(post=post).exists())
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'liked': liked,
        'tags_colors': settings.TAGS_COLORS,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        form.save_m2m()
        return redirect('posts:profile', post.author.username)

    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    if author != request.user:
        return redirect('posts:post_detail', post_id)
    else:
        post.delete()
        return redirect('posts:profile', author.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        form.save_m2m()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if (post.author != request.user
            and not request.user.liker.filter(post=post).exists()):
        Like.objects.create(
            user=request.user,
            post=post
        )
    return redirect('posts:post_detail', post_id)


@login_required
def post_unlike(request, post_id):
    Like.objects.filter(
        post=get_object_or_404(Post, id=post_id),
        user=request.user
    ).delete()
    return redirect('posts:post_detail', post_id)


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
def del_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    author = comment.author
    if author != request.user:
        return redirect('posts:post_detail', comment.post.id)
    else:
        comment.delete()
    return redirect('posts:post_detail', comment.post.id)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (author != request.user
            and not request.user.follower.filter(author=author).exists()):
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        author=get_object_or_404(User, username=username),
        user=request.user
    ).delete()
    return redirect('posts:profile', username)
