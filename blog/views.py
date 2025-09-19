from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from .models import Post, Presentation, Subject, PeerReviewRequest, Comment, Profile, Notification, Tag, Announcement
from .forms import PostForm, PresentationForm, CommentForm, PeerReviewRequestForm, ProfileForm, PrivateFeedbackForm, PostReviewStatusForm
from django.db.models import Q
from django.utils import timezone
from django.db.models.functions import ExtractYear
from datetime import date, timedelta

def timeline_redirect(request):
    # If the user is a student, redirect them to their personal timeline.
    if request.user.is_authenticated and request.user.groups.filter(name='Students').exists():
        return redirect('author_post_list', username=request.user.username)

    # Otherwise, show the public timeline for guests and teachers.
    return redirect('public_timeline')

def public_timeline(request):
    all_posts = Post.objects.filter(status='published').order_by('-created_date')
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
            post.status = request.POST.get('status', 'draft')
            post.save()

            tag_names = form.cleaned_data['tags'].split(',')
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                post.tags.add(tag)

            return redirect('timeline_redirect')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

def author_post_list(request, username, year=None):
    author = get_object_or_404(User, username=username)
    
    posts_list = Post.objects.filter(author=author).order_by('-created_date')
    if year:
        posts_list = posts_list.filter(created_date__year=year)
        
    drafts = posts_list.filter(status='draft')
    published = posts_list.filter(status='published')
        
    presentations = Presentation.objects.filter(author=author)
    portfolios = Portfolio.objects.filter(author=author)
    profile = Profile.objects.get_or_create(user=author)[0]
    
    archive_years = Post.objects.filter(author=author).annotate(year=ExtractYear('created_date')).values_list('year', flat=True).distinct().order_by('-year')

    # Fetch pending peer review requests
    pending_reviews = PeerReviewRequest.objects.filter(reviewer=author, status='pending')

    context = {
        'author': author,
        'drafts': drafts,
        'published': published,
        'presentations': presentations,
        'portfolios': portfolios,
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
            post = form.save(commit=False)
            post.status = request.POST.get('status', 'draft')
            post.save()

            post.tags.clear()
            tag_names = form.cleaned_data['tags'].split(',')
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                post.tags.add(tag)

            return redirect('author_post_list', username=request.user.username)
    else:
        form = PostForm(instance=post, initial={'tags': ', '.join([t.name for t in post.tags.all()])})
    return render(request, 'blog/post_form.html', {'form': form})

def is_teacher(user):
    return user.groups.filter(name='Teachers').exists()

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request, username=None):
    student_posts = Post.objects.filter(author__groups__name='Students')
    selected_student = None
    search_query = request.GET.get('q')
    selected_status = request.GET.get('status')

    if username:
        selected_student = get_object_or_404(User, username=username)
        student_posts = student_posts.filter(author=selected_student)

    if search_query:
        student_posts = student_posts.filter(
            Q(title__icontains=search_query) |
            Q(video_description__icontains=search_query)
        )

    if selected_status:
        student_posts = student_posts.filter(review_status=selected_status)

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

    # Contribution graph data
    today = date.today()
    start_date = today - timedelta(days=365)
    
    posts_last_year = student_posts.filter(created_date__date__gte=start_date)
    total_posts_last_year = posts_last_year.count()

    is_current_year = True
    for post in posts_last_year:
        if post.created_date.year != today.year:
            is_current_year = False
            break

    posts_by_date = {}
    for post in posts_last_year:
        day = post.created_date.date()
        posts_by_date[day] = posts_by_date.get(day, 0) + 1

    # Find the busiest day
    busiest_day = None
    if posts_by_date:
        busiest_day = max(posts_by_date, key=posts_by_date.get)

    # Generate heatmap structure
    heatmap = []
    current_date = start_date - timedelta(days=start_date.weekday())
    if start_date.weekday() == 6: # Start on Sunday
        current_date = start_date

    for _ in range(53): # 53 weeks to be safe
        week = []
        for i in range(7):
            day_count = posts_by_date.get(current_date, 0)
            
            level = 0
            if day_count > 0:
                level = 1
            if day_count > 2:
                level = 2
            if day_count > 5:
                level = 3
            if day_count > 8:
                level = 4

            week.append({
                'date': current_date,
                'count': day_count,
                'level': level,
                'is_future': current_date > today
            })
            current_date += timedelta(days=1)
        heatmap.append(week)

    # Generate month labels
    month_labels = []
    last_month_num = -1
    for week in heatmap:
        # Get the month from the first day of the week that is not in the future
        for day in week:
            if not day['is_future']:
                current_month_num = day['date'].month
                if current_month_num != last_month_num:
                    month_labels.append(day['date'].strftime('%b'))
                    last_month_num = current_month_num
                break # Move to the next week

    context = {
        'subject_posts': subject_posts,
        'students': students,
        'selected_student': selected_student,
        'search_query': search_query,
        'selected_status': selected_status,
        'subject_distribution': subject_distribution,
        'total_posts': total_posts,
        'heatmap': heatmap,
        'total_posts_last_year': total_posts_last_year,
        'start_date': start_date,
        'today': today,
        'month_labels': month_labels,
        'busiest_day': busiest_day,
        'busiest_day_count': posts_by_date.get(busiest_day, 0),
        'is_current_year': is_current_year,
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
                # Create a notification for the reviewer
                Notification.objects.create(
                    recipient=reviewer,
                    sender=request.user,
                    post=post,
                    message=f'{request.user.username} requested you to review their post "{post.title}".'
                )
            return redirect('post_detail', pk=post.pk)
    else:
        form = PeerReviewRequestForm(user=request.user)

    context = {
        'form': form,
        'post': post
    }
    return render(request, 'blog/request_peer_review.html', context)

from .forms import PostForm, PresentationForm, CommentForm, PeerReviewRequestForm, ProfileForm, PrivateFeedbackForm, PostReviewStatusForm, AnnouncementForm

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.view_count += 1
    post.save(update_fields=['view_count'])

    comment_form = None
    private_feedback_form = None
    review_status_form = None
    
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Comment form submission
            if 'comment_submit' in request.POST:
                comment_form = CommentForm(request.POST)
                if comment_form.is_valid():
                    new_comment = comment_form.save(commit=False)
                    new_comment.post = post
                    new_comment.author = request.user
                    new_comment.save()

                    if request.user.groups.filter(name='Students').exists():
                        PeerReviewRequest.objects.filter(
                            post=post,
                            reviewer=request.user,
                            status='pending'
                        ).update(status='completed')
                    return redirect('post_detail', pk=post.pk)

            # Private feedback form submission for teachers
            if is_teacher(request.user) and 'feedback_submit' in request.POST:
                private_feedback_form = PrivateFeedbackForm(request.POST)
                if private_feedback_form.is_valid():
                    new_feedback = private_feedback_form.save(commit=False)
                    new_feedback.post = post
                    new_feedback.author = request.user
                    new_feedback.save()

                    # Create a notification for the post author
                    Notification.objects.create(
                        recipient=post.author,
                        sender=request.user,
                        post=post,
                        message=f'{request.user.username} left private feedback on your post "{post.title}".'
                    )

                    return redirect('post_detail', pk=post.pk)

            # Review status form submission for teachers
            if is_teacher(request.user) and 'status_submit' in request.POST:
                review_status_form = PostReviewStatusForm(request.POST, instance=post)
                if review_status_form.is_valid():
                    review_status_form.save()

                    # Create a notification for the post author
                    Notification.objects.create(
                        recipient=post.author,
                        sender=request.user,
                        post=post,
                        message=f'The status of your post "{post.title}" has been changed to "{post.get_review_status_display()}".'
                    )

                    return redirect('post_detail', pk=post.pk)

        comment_form = CommentForm()
        if is_teacher(request.user):
            private_feedback_form = PrivateFeedbackForm()
            review_status_form = PostReviewStatusForm(instance=post)

    private_feedback = post.private_feedback.all() if request.user == post.author or (request.user.is_authenticated and is_teacher(request.user)) else []

    context = {
        'post': post,
        'comment_form': comment_form,
        'private_feedback': private_feedback,
        'private_feedback_form': private_feedback_form,
        'review_status_form': review_status_form,
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

from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    success_message = "Your password has been changed successfully."

@login_required
def presentation_delete(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    if presentation.author != request.user:
        return redirect('timeline_redirect')
    
    if request.method == 'POST':
        presentation.delete()
        return redirect('author_post_list', username=request.user.username)
        
    return render(request, 'blog/presentation_confirm_delete.html', {'presentation': presentation})

@login_required
@user_passes_test(is_teacher)
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()

            # Create notifications for all students
            students_group = Group.objects.get(name='Students')
            for student in students_group.user_set.all():
                Notification.objects.create(
                    recipient=student,
                    sender=request.user,
                    message=f'New Announcement: {announcement.title}'
                )

            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'blog/announcement_form.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def announcement_list(request):
    announcements = Announcement.objects.all().order_by('-created_date')
    context = {
        'announcements': announcements
    }
    return render(request, 'blog/announcement_list.html', context)

@login_required
def mark_notifications_as_read(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
    return redirect(request.META.get('HTTP_REFERER', 'timeline_redirect'))

def posts_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    posts = Post.objects.filter(tags=tag, status='published').order_by('-created_date')
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'tag': tag,
    }
    return render(request, 'blog/post_list.html', context)

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Portfolio
from .forms import PortfolioForm
from django.urls import reverse_lazy

class PortfolioListView(LoginRequiredMixin, ListView):
    model = Portfolio
    template_name = 'blog/portfolio_list.html'
    context_object_name = 'portfolios'

    def get_queryset(self):
        return Portfolio.objects.filter(author=self.request.user)

class PortfolioDetailView(DetailView):
    model = Portfolio
    template_name = 'blog/portfolio_detail.html'
    context_object_name = 'portfolio'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = self.get_object()
        context['published_posts'] = portfolio.posts.filter(status='published')
        context['draft_posts'] = portfolio.posts.filter(status='draft')
        context['presentations'] = portfolio.presentations.all()
        return context

class PortfolioCreateView(LoginRequiredMixin, CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'blog/portfolio_form.html'
    success_url = reverse_lazy('portfolio_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PortfolioUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'blog/portfolio_form.html'
    success_url = reverse_lazy('portfolio_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        portfolio = self.get_object()
        return self.request.user == portfolio.author

class PortfolioDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Portfolio
    template_name = 'blog/portfolio_confirm_delete.html'
    success_url = reverse_lazy('portfolio_list')

    def test_func(self):
        portfolio = self.get_object()
        return self.request.user == portfolio.author

class PublicPortfolioDetailView(DetailView):
    model = Portfolio
    template_name = 'blog/public_portfolio_detail.html'
    context_object_name = 'portfolio'

    def get_queryset(self):
        return Portfolio.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = self.get_object()
        context['posts'] = portfolio.posts.filter(status='published')
        context['presentations'] = portfolio.presentations.all()
        return context
