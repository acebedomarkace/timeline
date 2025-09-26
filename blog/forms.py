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

class CustomClearableFileInput(forms.ClearableFileInput):
    template_with_initial = (
        '%(initial_text)s: <a href="%(initial_url)s">%(initial)s</a> '
        '<br />%(input_text)s: %(input)s'
    )

class PostForm(forms.ModelForm):
    tags = forms.CharField(max_length=200, required=False, help_text='Enter comma-separated tags.')

    class Meta:
        model = Post
        fields = ['subject', 'title', 'content', 'photo', 'audio_file', 'youtube_url', 'video_file', 'media_description', 'tags']
        widgets = {
            'photo': CustomClearableFileInput,
            'audio_file': CustomClearableFileInput,
            'video_file': CustomClearableFileInput,
        }

    def __init__(self, *args, **kwargs):
        self.post_type = kwargs.pop('post_type', None)
        super().__init__(*args, **kwargs)

        if self.data:
            self.post_type = self.data.get('post_type')

        # Un-require fields that are dynamically shown/hidden
        self.fields['content'].required = False
        self.fields['photo'].required = False
        self.fields['video_file'].required = False
        self.fields['youtube_url'].required = False

        # Require the correct field based on post_type
        if self.post_type == 'journal':
            self.fields['content'].required = True
        elif self.post_type == 'photo':
            self.fields['photo'].required = True

    def clean(self):
        cleaned_data = super().clean()
        if self.post_type == 'video':
            if not cleaned_data.get('video_file') and not cleaned_data.get('youtube_url'):
                raise forms.ValidationError("For a video post, you must provide either a video file or a YouTube URL.")
        return cleaned_data

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