from django.contrib import admin
from .models import Subject, Post, Comment, Profile, Portfolio

admin.site.register(Subject)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(Portfolio)

