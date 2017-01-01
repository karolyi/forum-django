# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_auto_20151011_2017'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentVote',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('value', models.SmallIntegerField(verbose_name='Value')),
                ('comment', models.ForeignKey(verbose_name='Comment', to='base.Comment')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Comment vote',
                'verbose_name_plural': 'Comment votes',
            },
        ),
        migrations.CreateModel(
            name='UserReview',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('is_enabled', models.BooleanField(verbose_name='Is approved', default=False)),
                ('value', models.PositiveSmallIntegerField(verbose_name='Value')),
                ('created_at', models.DateTimeField(verbose_name='Created at', auto_now_add=True)),
                ('content_html', models.TextField(verbose_name='HTML content')),
                ('content_md', models.TextField(verbose_name='Markdown content')),
                ('ratee', models.ForeignKey(verbose_name='Ratee', related_name='ratee', to=settings.AUTH_USER_MODEL)),
                ('rater', models.ForeignKey(verbose_name='Rater', related_name='rater', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User rating',
                'verbose_name_plural': 'User ratings',
            },
        ),
        migrations.AlterUniqueTogether(
            name='commentvote',
            unique_together=set([('comment', 'user')]),
        ),
    ]
