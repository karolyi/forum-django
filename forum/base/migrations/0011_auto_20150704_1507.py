# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0001_initial'),
        ('cdn', '0009_auto_20150704_1507'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0010_auto_20150525_2043'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', django_extensions.db.fields.AutoSlugField(editable=False, blank=True, populate_from=('username',), verbose_name='Slug of the user', unique=True)),
                ('last_global_read', models.PositiveIntegerField(verbose_name='Last global message ID read')),
                ('received_comment_vote_sum', models.IntegerField(verbose_name='Summary received votes value on comments')),
                ('received_comment_vote_count', models.PositiveIntegerField(verbose_name='Summary received votes count on comments')),
                ('comment_vote_hide_limit', models.IntegerField(default=-5, verbose_name='Hide comments under this vote value')),
                ('quote', models.CharField(max_length=256, verbose_name='Chosen quote (appears at username)')),
                ('max_comments_per_day', models.PositiveIntegerField(verbose_name='Maximum allowed comments per day')),
                ('comment_count', models.PositiveIntegerField(verbose_name='Comment count')),
                ('invitations_today', models.PositiveIntegerField(verbose_name='Sent invitations today')),
                ('invitations_success', models.PositiveIntegerField(verbose_name='Successful invitations')),
                ('pw_reminders_today', models.PositiveIntegerField(verbose_name='Password reminders sent today')),
                ('used_skin', models.CharField(max_length=256, verbose_name='Used skin name')),
                ('introduction_all', models.TextField(verbose_name='Introduction visible for everybody')),
                ('introduction_reg', models.TextField(verbose_name='Introduction visible for registered users')),
                ('introduction_friends', models.TextField(verbose_name='Introduction visible for friended users')),
                ('picture_emails', models.CharField(max_length=256, verbose_name='Email addresses used for image upload separated with semicolon (;)')),
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
                ('ignored_users', models.ManyToManyField(verbose_name='List of ignored users', to='base.Settings', related_name='ignored_users_rel_+', null=None)),
                ('inviter', models.ForeignKey(default=None, null=True, to='base.Settings', verbose_name='Invited by')),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='ignored_users',
        ),
        migrations.RemoveField(
            model_name='user',
            name='inviter',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_ptr',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='settings',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, verbose_name='Respective user'),
        ),
    ]
