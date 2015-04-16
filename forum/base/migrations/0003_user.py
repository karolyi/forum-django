# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('base', '0002_auto_20150415_1650'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, serialize=False, to=settings.AUTH_USER_MODEL, primary_key=True, auto_created=True)),
                ('last_global_read', models.PositiveIntegerField(verbose_name='Last global message ID read')),
                ('received_comment_vote_sum', models.IntegerField(verbose_name='Summary received votes value on comments')),
                ('received_comment_vote_count', models.PositiveIntegerField(verbose_name='Summary received votes count on comments')),
                ('comment_vote_hide_limit', models.IntegerField(default=-5, verbose_name='Hide comments under this vote value')),
                ('quote', models.CharField(verbose_name='Chosen quote (appears at username)', max_length=256)),
                ('max_comments_per_day', models.PositiveIntegerField(verbose_name='Maximum allowed comments per day')),
                ('comment_count', models.PositiveIntegerField(verbose_name='Comment count')),
                ('todays_comment_count', models.PositiveIntegerField(verbose_name="Today's comment count")),
                ('invitations_today', models.PositiveIntegerField(verbose_name='Sent invitations today')),
                ('invitations_success', models.PositiveIntegerField(verbose_name='Successful invitations')),
                ('pw_reminders_today', models.PositiveIntegerField(verbose_name='Password reminders sent today')),
                ('used_skin', models.CharField(verbose_name='Used skin name', max_length=256)),
                ('introduction_all', models.TextField(verbose_name='Introduction visible for everybody')),
                ('introduction_reg', models.TextField(verbose_name='Introduction visible for registered users')),
                ('introduction_friends', models.TextField(verbose_name='Introduction visible for friended users')),
                ('picture_emails', models.CharField(verbose_name='Email addresses used for image upload separated with semicolon (;)', max_length=256)),
                ('uses_auto_bookmarks', models.BooleanField(default=False, verbose_name='Use automatic bookmark placement')),
                ('mails_own_topic_comments', models.BooleanField(default=False, verbose_name='Receive mails from comments in own topic')),
                ('mails_replies_topic', models.BooleanField(default=True, verbose_name='Receive mails from comment replies')),
                ('mails_moderation_topic', models.BooleanField(default=True, verbose_name='Receive mails from moderation')),
                ('mails_messages', models.BooleanField(default=True, verbose_name='Receive mails from messages')),
                ('show_replies_comment', models.BooleanField(default=True, verbose_name='Show replies on comments')),
                ('show_relations', models.BooleanField(default=True, verbose_name='Show user relations')),
                ('is_banned', models.BooleanField(default=False, verbose_name='User is banned')),
                ('separate_bookmarked_topics', models.BooleanField(default=True, verbose_name='Show bookmarked topics separated')),
                ('show_outsiders', models.BooleanField(default=True, verbose_name='Show not-logged-in users')),
                ('has_chat_enabled', models.BooleanField(default=True, verbose_name='Enable chat')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Is approved by admins')),
                ('expand_archived', models.BooleanField(default=False, verbose_name='Expand archived topics')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
