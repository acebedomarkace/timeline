from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from .models import Post, Presentation, Subject, PeerReviewRequest, Comment, Profile
from .forms import PostForm, PresentationForm, CommentForm, PeerReviewRequestForm, ProfileForm
from django.db.models import Q
from django.utils import timezone
from django.db.models.functions import ExtractYear

def timeline_redirect(request):
    # If the user is a student, redirect them to their personal timeline.
    if request.user.is_authenticated and request.user.groups.filter(name='Students').exists():
        return redirect('author_post_list', username=request.user.username)

    # Otherwise, show the public timeline for guests and teachers.
    return redirect('public_timeline')

def public_timeline(request):
    all_posts = Post.objects.order_by('-created_date')
    paginator = Paginator(all_posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
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
            return redirect('timeline_redirect')
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
            return redirect('timeline_redirect')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

def author_post_list(request, username, year=None):
    author = get_object_or_404(User, username=username)
    
    posts = Post.objects.filter(author=author).order_by('-created_date')
    if year:
        posts = posts.filter(created_date__year=year)
        
    presentations = Presentation.objects.filter(author=author)
    profile = Profile.objects.get_or_create(user=author)[0]
    
    archive_years = Post.objects.filter(author=author).annotate(year=ExtractYear('created_date')).values_list('year', flat=True).distinct().order_by('-year')

    # Fetch pending peer review requests
    pending_reviews = PeerReviewRequest.objects.filter(reviewer=author, status='pending')

    context = {
        'author': author,
        'posts': posts,
        'presentations': presentations,
        'profile': profile,
        'archive_years': archive_years,
        'selected_year': year,
        'pending_reviews': pending_reviews,
        'current_year': timezone.now().year
    }
    return render(request, 'blog/author_post_list.html', context)

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('timeline_redirect')
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
def teacher_dashboard(request, username=None):
    student_posts = Post.objects.filter(author__groups__name='Students')
    selected_student = None
    search_query = request.GET.get('q')

    if username:
        selected_student = get_object_or_404(User, username=username)
        student_posts = student_posts.filter(author=selected_student)

    if search_query:
        student_posts = student_posts.filter(
            Q(title__icontains=search_query) |
            Q(video_description__icontains=search_query)
        )

    subjects = Subject.objects.filter(post__in=student_posts).distinct().prefetch_related('post_set')
    
    subject_posts = {subject: subject.post_set.filter(id__in=student_posts).order_by('-created_date') for subject in subjects}

    students = User.objects.filter(groups__name='Students').order_by('username')

    # Calculate subject distribution
    total_posts = student_posts.count()
    subject_distribution = {}
    if total_posts > 0:
        for subject in subjects:
            post_count = subject_posts[subject].count()
            percentage = (post_count / total_posts) * 100
            subject_distribution[subject.name] = round(percentage, 1)

    context = {
        'subject_posts': subject_posts,
        'students': students,
        'selected_student': selected_student,
        'search_query': search_query,
        'subject_distribution': subject_distribution,
        'total_posts': total_posts,
    }
    return render(request, 'blog/teacher_dashboard.html', context)

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('timeline_redirect')
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
    
    # Group posts by subject
    subject_posts = {}
    for post in presentation.posts.all().order_by('subject__name', '-created_date'):
        if post.subject not in subject_posts:
            subject_posts[post.subject] = []
        subject_posts[post.subject].append(post)

    context = {
        'presentation': presentation,
        'subject_posts': subject_posts
    }
    return render(request, 'blog/presentation_detail.html', context)

@login_required
def request_peer_review(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('timeline_redirect')

    if request.method == 'POST':
        form = PeerReviewRequestForm(request.POST, user=request.user)
        if form.is_valid():
            reviewers = form.cleaned_data['reviewers']
            for reviewer in reviewers:
                PeerReviewRequest.objects.get_or_create(
                    post=post,
                    requester=request.user,
                    reviewer=reviewer
                )
            return redirect('post_detail', pk=post.pk)
    else:
        form = PeerReviewRequestForm(user=request.user)

    context = {
        'form': form,
        'post': post
    }
    return render(request, 'blog/request_peer_review.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.view_count += 1
    post.save(update_fields=['view_count'])

    comment_form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.post = post
                new_comment.author = request.user
                new_comment.save()

                # If the commenter is a student, check for a review request
                if request.user.groups.filter(name='Students').exists():
                    PeerReviewRequest.objects.filter(
                        post=post,
                        reviewer=request.user,
                        status='pending'
                    ).update(status='completed')

                return redirect('post_detail', pk=post.pk)
        comment_form = CommentForm()

    context = {
        'post': post,
        'comment_form': comment_form
    }
    return render(request, 'blog/post_detail.html', context)

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('author_post_list', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'blog/edit_profile.html', {'form': form})

@login_required
def presentation_edit(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    if presentation.author != request.user:
        return redirect('timeline_redirect')
    
    if request.method == 'POST':
        form = PresentationForm(request.POST, user=request.user, instance=presentation)
        if form.is_valid():
            form.save()
            return redirect('author_post_list', username=request.user.username)
    else:
        form = PresentationForm(user=request.user, instance=presentation)
    
    context = {
        'form': form,
        'presentation': presentation
    }
    return render(request, 'blog/presentation_form.html', context)

@login_required
def presentation_delete(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    if presentation.author != request.user:
        return redirect('timeline_redirect')
    
    if request.method == 'POST':
        presentation.delete()
        return redirect('author_post_list', username=request.user.username)
        
    return render(request, 'blog/presentation_confirm_delete.html', {'presentation': presentation})
