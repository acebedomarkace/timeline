from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_test_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')

    students_group, _ = Group.objects.get_or_create(name='Students')
    teachers_group, _ = Group.objects.get_or_create(name='Teachers')

    student_user, created = User.objects.get_or_create(
        username='student',
        defaults={
            'password': make_password('password'),
            'is_staff': False,
            'is_superuser': False,
        }
    )
    if created:
        students_group.user_set.add(student_user)

    teacher_user, created = User.objects.get_or_create(
        username='teacher',
        defaults={
            'password': make_password('password'),
            'is_staff': True,
            'is_superuser': False,
        }
    )
    if created:
        teachers_group.user_set.add(teacher_user)

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0022_portfolio_description'),
    ]

    operations = [
        migrations.RunPython(create_test_users),
    ]