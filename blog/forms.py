from django import forms
from .models import Post, Presentation, Comment, PeerReviewRequest, Profile, PrivateFeedback, Announcement, Portfolio, Family

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['theme', 'image']

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['name']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content']

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['title', 'description', 'posts', 'presentations', 'is_public']
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
        fields = ['subject', 'title', 'content', 'photo', 'audio_file', 'youtube_url', 'video_file', 'media_description', 'tags']

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

class JoinFamilyForm(forms.Form):
    invite_code = forms.CharField(label='Invite Code', max_length=20)

from django.db.models import Q

class PeerReviewRequestForm(forms.Form):
    reviewers = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Select classmates or teachers to request a review from"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['reviewers'].queryset = User.objects.filter(
            Q(groups__name='Students') | Q(groups__name='Teachers')
        ).exclude(id=user.id)
