# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now=True, verbose_name='Commented at')),
                ('number', models.PositiveIntegerField(verbose_name='Comment number in topic')),
                ('voting_value', models.SmallIntegerField(verbose_name='Value of up/downvotes')),
                ('content', models.TextField(verbose_name='Content')),
                ('host', models.CharField(max_length=256, verbose_name='Host of the commenter (old)')),
                ('ip', models.GenericIPAddressField(verbose_name='IP of the commenter')),
                ('unique_id', models.CharField(default=0, max_length=20, unique=True, verbose_name='Obsolete unique ID')),
            ],
        ),
        migrations.CreateModel(
            name='Edit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True, verbose_name='Edit timestamp')),
                ('diff', models.TextField(verbose_name='Diff of the previous version')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html', models.CharField(max_length=256, verbose_name='HTML name')),
                ('text', models.CharField(max_length=256, verbose_name='Text name')),
                ('is_disabled', models.BooleanField(default=True, verbose_name='Is topic disabled')),
                ('is_staff_only', models.BooleanField(default=False, verbose_name='Is staff only')),
                ('is_voting_enabled', models.BooleanField(default=True, verbose_name='Is voting enabled')),
                ('truncate_at', models.SmallIntegerField(null=True, verbose_name='Max comment number to keep')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last updated')),
                ('slug', models.SlugField(verbose_name='Topic slug')),
                ('comment_count', models.PositiveIntegerField(verbose_name='Comment count')),
                ('description', models.TextField(verbose_name='HTML description')),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Topic creator')),
                ('last_comment', models.ForeignKey(related_name='last_comment', to='forum_base.Comment', verbose_name='Last comment reference')),
                ('reply_to', models.ForeignKey(default=None, null=True, to='forum_base.Topic', verbose_name='Reply to topic goes to')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='edits',
            field=models.ForeignKey(to='forum_base.Edit', verbose_name='Edits'),
        ),
        migrations.AddField(
            model_name='comment',
            name='moved_from',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='moved_from', to='forum_base.Topic', verbose_name='Comment moved from topic'),
        ),
        migrations.AddField(
            model_name='comment',
            name='prev_comment',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='forum_base.Comment', verbose_name='Answered comment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='topic',
            field=models.ForeignKey(to='forum_base.Topic', verbose_name='Commented in topic'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='The commenter user'),
        ),
    ]
