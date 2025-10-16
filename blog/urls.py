from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('password_change/', views.CustomPasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url=reverse_lazy('timeline_redirect')
    ), name='password_change'),
    path('', views.timeline_redirect, name='timeline_redirect'),
    path('tag/<str:tag_name>/', views.posts_by_tag, name='posts_by_tag'),
    path('public-timeline/', views.public_timeline, name='public_timeline'),
    path('notifications/mark-as-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('archive/<int:year>/', views.public_timeline, name='post_list_archive'),
    path('signup/', views.signup, name='signup'),
    path('family/create/', views.family_create, name='family_create'),
    path('family/manage/', views.family_management, name='family_management'),
    path('family/join-or-create/', views.join_or_create_family, name='join_or_create_family'),
    path('family/join/', views.join_family, name='join_family'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/request-review/', views.request_peer_review, name='request_peer_review'),
    path('post/<int:pk>/assess/', views.assess_post, name='assess_post'),
    path('author/<str:username>/<int:year>/', views.author_post_list, name='author_post_list_by_year'),
    path('author/<str:username>/', views.author_post_list, name='author_post_list'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/dashboard/<str:username>/', views.teacher_dashboard, name='teacher_dashboard_filtered'),
    path('announcements/new/', views.announcement_create, name='announcement_create'),
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('presentation/new/', views.presentation_create, name='presentation_create'),
    path('presentation/<int:pk>/', views.presentation_detail, name='presentation_detail'),
    path('presentation/<int:pk>/edit/', views.presentation_edit, name='presentation_edit'),
    path('presentation/<int:pk>/delete/', views.presentation_delete, name='presentation_delete'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('tag/<str:tag_name>/', views.posts_by_tag, name='posts_by_tag'),

    # Portfolio URLs
    path('portfolio/', views.PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolio/new/', views.PortfolioCreateView.as_view(), name='portfolio_create'),
    path('portfolio/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('portfolio/<int:pk>/edit/', views.PortfolioUpdateView.as_view(), name='portfolio_edit'),
    path('portfolio/<int:pk>/delete/', views.PortfolioDeleteView.as_view(), name='portfolio_delete'),
    path('portfolio/public/<int:pk>/', views.PublicPortfolioDetailView.as_view(), name='public_portfolio_detail'),

    # Rubric URLs
    path('rubrics/', views.rubric_list, name='rubric_list'),
    path('rubrics/create/', views.rubric_create, name='rubric_create'),
    path('rubrics/<int:pk>/', views.rubric_detail, name='rubric_detail'),
    path('rubrics/<int:pk>/edit/', views.rubric_edit, name='rubric_edit'),
    path('rubrics/<int:pk>/delete/', views.rubric_delete, name='rubric_delete'),
]