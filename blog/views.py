from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from .models import Post, Presentation, Subject, PeerReviewRequest, Comment, Profile, Notification, Tag, Announcement, Family, PresentationPost
from .forms import PostForm, PresentationForm, CommentForm, PeerReviewRequestForm, ProfileForm, PrivateFeedbackForm, PostReviewStatusForm, FamilyForm, JoinFamilyForm
from django.db.models import Q
from django.utils import timezone
from django.db.models.functions import ExtractYear
from datetime import date, timedelta
import secrets
import string
from django.contrib import messages

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
            return redirect('join_or_create_family')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def post_create(request):
    post_type = request.GET.get('type', 'journal')
    
    if request.method == 'POST':
        print(f"POST data: {request.POST}")  # Debug
        form = PostForm(request.POST, request.FILES, post_type=post_type)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.post_type = post_type
            
            # Handle action buttons
            action = request.POST.get('action')
            post.status = 'published' if action == 'publish' else 'draft'
            post.save()
            
            # Handle tags safely
            tags_data = form.cleaned_data.get('tags', '')
            if tags_data:
                post.tags.clear()
                tag_names = [t.strip() for t in str(tags_data).split(',') if t.strip()]
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
            
            messages.success(request, f"Post {'published' if action == 'publish' else 'saved as draft'}!")
            return redirect('author_post_list', username=request.user.username)
        else:
            print(f"Form errors: {form.errors}")  # Debug
            messages.error(request, "Please fix form errors.")
    else:
        form = PostForm(post_type=post_type)
    
    return render(request, 'blog/post_form.html', {'form': form, 'post_type': post_type})

def author_post_list(request, username, year=None):
    author = get_object_or_404(User, username=username)

    # Defensively get or create profiles to prevent crashes for users made before profile signal.
    requesting_user_profile, _ = Profile.objects.get_or_create(user=request.user)
    author_profile, _ = Profile.objects.get_or_create(user=author)

    # Multi-tenancy security check
    if not requesting_user_profile.family:
        return redirect('family_create')

    if requesting_user_profile.family != author_profile.family:
        return redirect('timeline_redirect')
    
    posts_list = Post.objects.filter(author=author).order_by('-created_date')
    if year:
        posts_list = posts_list.filter(created_date__year=year)
        
    # Tag filtering
    all_tags = Tag.objects.filter(post__author=author).distinct()
    active_tag_slug = request.GET.get('tag')
    active_tag = None
    if active_tag_slug:
        active_tag = get_object_or_404(Tag, slug=active_tag_slug)
        posts_list = posts_list.filter(tags=active_tag)

    status_filter = request.GET.get('status')
    if status_filter in ['published', 'draft']:
        posts_list = posts_list.filter(status=status_filter)
        
    presentations = Presentation.objects.filter(author=author)
    portfolios = Portfolio.objects.filter(author=author)
    
    archive_years = Post.objects.filter(author=author).annotate(year=ExtractYear('created_date')).values_list('year', flat=True).distinct().order_by('-year')

    # Fetch pending peer review requests
    pending_reviews = PeerReviewRequest.objects.filter(reviewer=author, status='pending')

    context = {
        'author': author,
        'posts': posts_list,
        'presentations': presentations,
        'portfolios': portfolios,
        'profile': author_profile, # Use the safely fetched profile
        'archive_years': archive_years,
        'selected_year': year,
        'pending_reviews': pending_reviews,
        'current_year': timezone.now().year,
        'status_filter': status_filter,
        'all_tags': all_tags,
        'active_tag': active_tag
    }
    return render(request, 'blog/author_post_list.html', context)

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('timeline_redirect')

    post_type = post.post_type

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post, post_type=post_type)
        if form.is_valid():
            post = form.save(commit=False)
            action = request.POST.get('action')
            if action == 'publish':
                post.status = 'published'
            else:
                post.status = 'draft'
            post.save()
            
            # Handle tags safely
            tags_data = form.cleaned_data.get('tags', '')
            if tags_data:
                post.tags.clear()
                tag_names = [t.strip() for t in str(tags_data).split(',') if t.strip()]
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
            
            messages.success(request, f'Post successfully updated as {post.status}.')
            return redirect('author_post_list', username=request.user.username) # Redirect after success
        else:
            messages.error(request, f'Please correct the errors below: {form.errors}')
    else:
        form = PostForm(instance=post, post_type=post_type, initial={'tags': ', '.join([t.name for t in post.tags.all()])})
    return render(request, 'blog/post_form.html', {'form': form, 'post_type': post_type})

def is_teacher(user):
    return user.groups.filter(name='Teachers').exists()

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request, username=None):
    requesting_user_profile, _ = Profile.objects.get_or_create(user=request.user)
    # Ensure the teacher has a family assigned
    if not requesting_user_profile.family:
        return redirect('family_create')

    family = requesting_user_profile.family
    student_posts = Post.objects.filter(author__groups__name='Students', author__profile__family=family)
    selected_student = None
    search_query = request.GET.get('q')
    selected_status = request.GET.get('status')

    if username:
        selected_student = get_object_or_404(User, username=username, profile__family=family)
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

    students = User.objects.filter(groups__name='Students', profile__family=family).order_by('username')

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
    # This logic now runs for GET requests and failed POSTs.
    all_subjects = Subject.objects.filter(post__author=request.user).distinct()

    if request.method == 'POST':
        form = PresentationForm(request.POST, user=request.user)
        if form.is_valid():
            presentation = form.save(commit=False)
            presentation.author = request.user
            presentation.save()
            
            # Save posts with their order
            for i, post_obj in enumerate(form.cleaned_data['posts']):
                PresentationPost.objects.create(presentation=presentation, post_id=post_obj.id, order=i)
            messages.success(request, 'Presentation created successfully!')
            return redirect('author_post_list', username=request.user.username)
        # If form is invalid, it falls through to render the page again,
        # now with the necessary context.
    else:
        form = PresentationForm(user=request.user)

    # Filter posts based on search and subject for display
    search_query = request.GET.get('q', '')
    subject_id = request.GET.get('subject', '')
    
    # Start with the base queryset from the form's initial definition
    posts_queryset = Post.objects.filter(author=request.user)
    if search_query:
        posts_queryset = posts_queryset.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )
    if subject_id:
        posts_queryset = posts_queryset.filter(subject__id=subject_id)

    # Update the form instance with the filtered posts for rendering


    context = {
        'form': form,
        'all_subjects': all_subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'posts': posts_queryset
    }
    return render(request, 'blog/presentation_form.html', context)

@login_required
def presentation_detail(request, pk):
    requesting_user_profile, _ = Profile.objects.get_or_create(user=request.user)
    presentation = get_object_or_404(Presentation, pk=pk, author__profile__family=requesting_user_profile.family)

    # Get all posts in the presentation, ordered by their order in PresentationPost
    all_posts = [pp.post for pp in presentation.presentationpost_set.all().order_by('order')]

    context = {
        'presentation': presentation,
        'all_posts': all_posts,  # Pass the ordered posts to the template
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
    print("--- DEBUG: post_detail VIEW IS RUNNING ---")
    post = get_object_or_404(Post, pk=pk)

    # Multi-tenancy and privacy security check
    if request.user.is_authenticated:
        requesting_user_profile, _ = Profile.objects.get_or_create(user=request.user)
        author_profile, _ = Profile.objects.get_or_create(user=post.author)
        if not requesting_user_profile.family or requesting_user_profile.family != author_profile.family:
            return redirect('timeline_redirect')
    elif post.status != 'published':
        # Anonymous users can only see published posts.
        return redirect('timeline_redirect')

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

    all_subjects = Subject.objects.filter(post__author=request.user).distinct()

    if request.method == 'POST':
        form = PresentationForm(request.POST, user=request.user, instance=presentation)
        if form.is_valid():
            presentation = form.save(commit=False)
            presentation.save()
            
            # Clear existing posts and save new ones with order
            presentation.presentationpost_set.all().delete()
            for i, post_obj in enumerate(form.cleaned_data['posts']):
                PresentationPost.objects.create(presentation=presentation, post_id=post_obj.id, order=i)
            messages.success(request, 'Presentation updated successfully!')
            return redirect('author_post_list', username=request.user.username)
    else:
        form = PresentationForm(user=request.user, instance=presentation)

    # Filtering logic for the Post Library
    search_query = request.GET.get('q', '')
    subject_id = request.GET.get('subject', '')
    
    posts_queryset = Post.objects.filter(author=request.user)
    if search_query:
        posts_queryset = posts_queryset.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )
    if subject_id:
        posts_queryset = posts_queryset.filter(subject__id=subject_id)


    
    # Get IDs of posts already in the presentation to pre-populate the storyboard
    existing_post_ids = list(presentation.posts.values_list('id', flat=True))

    context = {
        'form': form,
        'presentation': presentation,
        'all_subjects': all_subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'posts': posts_queryset
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
    requesting_user_profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()

            # Create notifications only for students in the same family
            if requesting_user_profile.family:
                students_group = Group.objects.get(name='Students')
                students_in_family = students_group.user_set.filter(profile__family=requesting_user_profile.family)
                for student in students_in_family:
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
    requesting_user_profile, _ = Profile.objects.get_or_create(user=request.user)
    if not requesting_user_profile.family:
        return render(request, 'blog/announcement_list.html', {'announcements': []})

    announcements = Announcement.objects.filter(author__profile__family=requesting_user_profile.family).order_by('-created_date')
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

@login_required
def family_create(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    # Users who are already in a family should not be able to create a new one.
    if profile.family:
        return redirect('timeline_redirect')

    if request.method == 'POST':
        form = FamilyForm(request.POST)
        if form.is_valid():
            family = form.save()
            # Assign the current user to this new family
            profile.family = family
            profile.save()
            return redirect('timeline_redirect')
    else:
        form = FamilyForm()
    
    return render(request, 'blog/family_form.html', {'form': form})

@login_required
def family_management(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.family:
        return redirect('family_create')

    family = profile.family

    if request.method == 'POST':
        # Generate a new unique invite code
        while True:
            # Generate a random code (e.g., ABC-123)
            code = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(3)) + '-' + ''.join(secrets.choice(string.digits) for _ in range(3))
            # Check if it's unique
            if not Family.objects.filter(invite_code=code).exists():
                family.invite_code = code
                family.save()
                break
        return redirect('family_management')

    return render(request, 'blog/family_management.html', {'family': family})

@login_required
def join_or_create_family(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    # If the user is already in a family, redirect them away.
    if profile.family:
        return redirect('timeline_redirect')

    context = {
        'has_family': profile.family is not None
    }
    return render(request, 'blog/join_or_create_family.html', context)

@login_required
def join_family(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    # If user is already in a family, they shouldn't be here.
    if profile.family:
        messages.info(request, "You are already part of a family.")
        return redirect('timeline_redirect')

    if request.method == 'POST':
        form = JoinFamilyForm(request.POST)
        if form.is_valid():
            invite_code = form.cleaned_data['invite_code']
            try:
                family = Family.objects.get(invite_code=invite_code)
                profile.family = family
                profile.save()
                messages.success(request, f'Successfully joined family {family.name}!')
                return redirect('timeline_redirect')
            except Family.DoesNotExist:
                messages.error(request, 'Invalid invite code.')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = JoinFamilyForm()
    
    return render(request, 'blog/join_family_form.html', {'form': form})
