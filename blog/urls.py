from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('password_change/', views.CustomPasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url=reverse_lazy('timeline_redirect')
    ), name='password_change'),
    path('', views.timeline_redirect, name='timeline_redirect'),
    path('public-timeline/', views.public_timeline, name='public_timeline'),
    path('archive/<int:year>/', views.public_timeline, name='post_list_archive'),
    path('signup/', views.signup, name='signup'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/request-review/', views.request_peer_review, name='request_peer_review'),
    path('author/<str:username>/<int:year>/', views.author_post_list, name='author_post_list_by_year'),
    path('author/<str:username>/', views.author_post_list, name='author_post_list'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/dashboard/<str:username>/', views.teacher_dashboard, name='teacher_dashboard_filtered'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('presentation/new/', views.presentation_create, name='presentation_create'),
    path('presentation/<int:pk>/', views.presentation_detail, name='presentation_detail'),
    path('presentation/<int:pk>/edit/', views.presentation_edit, name='presentation_edit'),
    path('presentation/<int:pk>/delete/', views.presentation_delete, name='presentation_delete'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]