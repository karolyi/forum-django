# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('messaging', '0003_mail_sender_deleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(verbose_name='Created at')),
                ('is_enabled', models.BooleanField(verbose_name='Is enabled')),
                ('subject', models.CharField(max_length=100, verbose_name='Subject')),
                ('content_html', models.TextField(verbose_name='HTML content')),
                ('content_md', models.TextField(verbose_name='Markdown content')),
                ('user', models.ForeignKey(verbose_name='Created by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Global messages',
                'verbose_name': 'Global message',
            },
        ),
    ]
