from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_more_students(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')

    students_group, _ = Group.objects.get_or_create(name='Students')

    users_to_create = [
        {'username': 'Kyp3r', 'password': 'password'},
        {'username': 'Liv', 'password': 'password'},
    ]

    for user_data in users_to_create:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'password': make_password(user_data['password']),
                'is_staff': False,
                'is_superuser': False,
            }
        )
        if created:
            students_group.user_set.add(user)

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0023_create_test_users'),
    ]

    operations = [
        migrations.RunPython(create_more_students),
    ]
