from django import forms
from .models import Post, Presentation

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['subject', 'title', 'content', 'photo', 'annotation', 'audio_file', 'audio_description']

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
