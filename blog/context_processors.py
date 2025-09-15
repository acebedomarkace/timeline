from .models import Notification

def user_roles(request):
    is_teacher = False
    if request.user.is_authenticated:
        is_teacher = request.user.groups.filter(name='Teachers').exists()
    return {'is_teacher': is_teacher}

def notifications(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(recipient=request.user, read=False).order_by('-created_date')
        return {
            'notifications': unread_notifications,
            'notification_count': unread_notifications.count(),
        }
    return {}
