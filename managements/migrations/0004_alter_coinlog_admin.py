# Generated by Django 3.2.5 on 2021-08-07 14:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('managements', '0003_coinlog_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coinlog',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coin_from_user', to=settings.AUTH_USER_MODEL, verbose_name='操作人'),
        ),
    ]
