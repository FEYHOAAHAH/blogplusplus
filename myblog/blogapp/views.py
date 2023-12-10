# views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Post
from .forms import PostForm


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('post_list')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def post_list(request):
    posts = Post.objects.all().order_by('-pub_date')
    return render(request, 'post_list.html', {'posts': posts})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.author or request.user.is_staff:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('post_list')
        else:
            form = PostForm(instance=post)

        return render(request, 'edit_post.html', {'post': post, 'form': form})
    else:
        return redirect('access_denied_page')


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удален.')
        return redirect('post_list')
    else:
        return render(request, 'delete_post.html', {'post': post})


def add_to_favorites(request, post_id):
    favorite_articles = request.session.get('favorite_articles', [])

    if post_id not in favorite_articles:
        favorite_articles.append(post_id)
        request.session['favorite_articles'] = favorite_articles

    return redirect('post_list')


