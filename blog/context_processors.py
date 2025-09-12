def user_roles(request):
    is_teacher = False
    if request.user.is_authenticated:
        is_teacher = request.user.groups.filter(name='Teachers').exists()
    return {'is_teacher': is_teacher}
