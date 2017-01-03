# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_rating', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRating',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('is_enabled', models.BooleanField(default=False, verbose_name='Is approved')),
                ('value', models.SmallIntegerField(verbose_name='Value')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('content_html', models.TextField(verbose_name='HTML content')),
                ('content_md', models.TextField(verbose_name='Markdown content')),
                ('ratee', models.ForeignKey(verbose_name='Ratee', to=settings.AUTH_USER_MODEL, related_name='ratee')),
                ('rater', models.ForeignKey(verbose_name='Rater', to=settings.AUTH_USER_MODEL, related_name='rater')),
            ],
            options={
                'verbose_name_plural': 'User ratings',
                'verbose_name': 'User rating',
            },
        ),
        migrations.RemoveField(
            model_name='userreview',
            name='ratee',
        ),
        migrations.RemoveField(
            model_name='userreview',
            name='rater',
        ),
        migrations.DeleteModel(
            name='UserReview',
        ),
    ]
