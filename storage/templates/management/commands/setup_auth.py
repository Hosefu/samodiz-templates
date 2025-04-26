from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from templates.models import UserGroup

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup initial admin user and groups'

    def handle(self, *args, **kwargs):
        # Создаем суперпользователя, если его нет
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write(self.style.WARNING('Admin user already exists'))
        
        # Создаем тестового пользователя, если его нет
        if not User.objects.filter(username='user').exists():
            user = User.objects.create_user(
                username='user',
                email='user@example.com',
                password='user123',
                role='user'
            )
            self.stdout.write(self.style.SUCCESS('Test user created successfully'))
        else:
            user = User.objects.get(username='user')
            self.stdout.write(self.style.WARNING('Test user already exists'))
        
        # Создаем группу, если ее нет
        if not UserGroup.objects.filter(name='Editors').exists():
            editors_group = UserGroup.objects.create(
                name='Editors',
                description='Users with edit permissions'
            )
            editors_group.members.add(user)
            self.stdout.write(self.style.SUCCESS('Editors group created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Editors group already exists')) 