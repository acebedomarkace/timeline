from django.contrib import admin
from .models import Subject, Post, Comment, Profile

admin.site.register(Subject)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Profile)

