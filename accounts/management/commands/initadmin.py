import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = os.environ.get('INIT_ADMIN_EMAIL', 'admin@example.com')
        nickname = os.environ.get('INIT_ADMIN_NICKNAME', 'admin')
        password = os.environ.get('INIT_ADMIN_PASSWORD', 'a123123123')

        if User.objects.count() == 0:
            print('Creating account for %s (%s)' % (nickname, email))
            User.objects.create_superuser(email=email, nickname=nickname, password=password)
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
