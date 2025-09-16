from django import forms
from .models import Post, Presentation, Comment, PeerReviewRequest, Profile, PrivateFeedback, Announcement, Portfolio

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['theme', 'image']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content']

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['title', 'posts', 'presentations', 'is_public']
        widgets = {
            'posts': forms.CheckboxSelectMultiple,
            'presentations': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['posts'].queryset = Post.objects.filter(author=user)
        self.fields['presentations'].queryset = Presentation.objects.filter(author=user)

from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    tags = forms.CharField(max_length=200, required=False, help_text='Enter comma-separated tags.')

    class Meta:
        model = Post
        fields = ['subject', 'title', 'content', 'photo', 'annotation', 'audio_file', 'audio_description', 'youtube_url', 'video_file', 'video_description', 'tags']

class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'posts', 'type']
        widgets = {
            'posts': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['posts'].queryset = Post.objects.filter(author=user)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

class PrivateFeedbackForm(forms.ModelForm):
    class Meta:
        model = PrivateFeedback
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

class PostReviewStatusForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['review_status']

class PeerReviewRequestForm(forms.Form):
    reviewers = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Select classmates to request a review from"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['reviewers'].queryset = User.objects.filter(groups__name='Students').exclude(id=user.id)
