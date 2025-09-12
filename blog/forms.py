from django import forms
from .models import Post, Presentation, Comment, PeerReviewRequest, Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['theme', 'image']

from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['subject', 'title', 'content', 'photo', 'annotation', 'audio_file', 'audio_description', 'youtube_url']

class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'posts']
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
