from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from .models import Post, Presentation
from .forms import PostForm, PresentationForm

def post_list(request):
    posts = Post.objects.order_by('-created_date')
    presentations = None
    if request.user.is_authenticated and request.user.groups.filter(name='Students').exists():
        posts = posts.filter(author=request.user)
        presentations = Presentation.objects.filter(author=request.user)
    
    context = {
        'posts': posts,
        'presentations': presentations
    }
    return render(request, 'blog/post_list.html', context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            students_group = Group.objects.get(name='Students')
            user.groups.add(students_group)
            login(request, user)
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

def author_post_list(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).order_by('-created_date')
    presentations = Presentation.objects.filter(author=author)
    return render(request, 'blog/author_post_list.html', {'author': author, 'posts': posts, 'presentations': presentations})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('post_list')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('author_post_list', username=request.user.username)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})

def is_teacher(user):
    return user.groups.filter(name='Teachers').exists()

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    students_group = Group.objects.get(name='Students')
    students = User.objects.filter(groups=students_group)
    return render(request, 'blog/teacher_dashboard.html', {'students': students})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('post_list')
    if request.method == 'POST':
        post.delete()
        return redirect('author_post_list', username=request.user.username)
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required
def presentation_create(request):
    if request.method == 'POST':
        form = PresentationForm(request.POST, user=request.user)
        if form.is_valid():
            presentation = form.save(commit=False)
            presentation.author = request.user
            presentation.save()
            form.save_m2m() # Necessary for ManyToManyFields
            return redirect('author_post_list', username=request.user.username)
    else:
        form = PresentationForm(user=request.user)
    return render(request, 'blog/presentation_form.html', {'form': form})

def presentation_detail(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    return render(request, 'blog/presentation_detail.html', {'presentation': presentation})
