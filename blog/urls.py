from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('signup/', views.signup, name='signup'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('author/<str:username>/', views.author_post_list, name='author_post_list'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('presentation/new/', views.presentation_create, name='presentation_create'),
    path('presentation/<int:pk>/', views.presentation_detail, name='presentation_detail'),
]

