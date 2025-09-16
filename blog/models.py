from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from urllib.parse import urlparse, parse_qs
from django.db.models.signals import post_save
from django.dispatch import receiver

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    REVIEW_STATUS_CHOICES = (
        ('needs_review', 'Needs Review'),
        ('revision_requested', 'Revision Requested'),
        ('approved', 'Approved'),
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    content = models.TextField()
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    annotation = models.TextField(blank=True, null=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    audio_description = models.TextField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_description = models.TextField(blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='needs_review')
    tags = models.ManyToManyField(Tag, blank=True)

    def get_youtube_embed_url(self):
        if not self.youtube_url:
            return None
        
        try:
            url_data = urlparse(self.youtube_url)
            query = parse_qs(url_data.query)
            video_id = None

            if 'youtube.com' in url_data.netloc:
                video_id = query.get('v', [None])[0]
            elif 'youtu.be' in url_data.netloc:
                video_id = url_data.path.lstrip('/')

            if video_id:
                return f'https://www.youtube.com/embed/{video_id}'
        except Exception:
            # If parsing fails for any reason, just return None
            return None
        
        return None

    def __str__(self):
        return self.title

class PrivateFeedback(models.Model):
    post = models.ForeignKey(Post, related_name='private_feedback', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Feedback by {self.author} on {self.post}'

class Presentation(models.Model):
    TYPE_CHOICES = [
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('showcase', 'Showcase'),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    posts = models.ManyToManyField(Post)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='project')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

class PeerReviewRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    requester = models.ForeignKey(User, related_name='review_requests_sent', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name='review_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('post', 'reviewer')

    def __str__(self):
        return f'Request for {self.post} from {self.requester} to {self.reviewer}'

class Profile(models.Model):
    THEME_CHOICES = [
        ('light', 'Default Light'),
        ('dark', 'Default Dark'),
        ('sepia', 'Sepia'),
        ('ocean', 'Ocean'),
        ('forest', 'Forest'),
        ('sunset', 'Sunset'),
        ('monochrome', 'Monochrome'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class Notification(models.Model):
    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Notification for {self.recipient.username}'

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.title

class Portfolio(models.Model):
    # Temporary change to force migration
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    posts = models.ManyToManyField(Post, blank=True)
    presentations = models.ManyToManyField(Presentation, blank=True)
    is_public = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

