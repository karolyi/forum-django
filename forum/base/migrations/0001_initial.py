# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('time', models.DateTimeField(verbose_name='Commented at', auto_now=True)),
                ('number', models.IntegerField(verbose_name='Comment number in topic')),
                ('voting_value', models.IntegerField(verbose_name='Value of up/downvotes')),
                ('content', models.TextField(verbose_name='Content')),
                ('host', models.CharField(verbose_name='Host of the commenter (old)', max_length=256)),
                ('ip', models.IPAddressField(verbose_name='IP of the commenter')),
                ('unique_id', models.CharField(verbose_name='Obsolete unique ID', max_length=20, default=0, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Edit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(verbose_name='Edit timestamp', auto_now=True)),
                ('diff', models.TextField(verbose_name='Diff of the previous version')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('html', models.CharField(verbose_name='HTML name', max_length=256)),
                ('text', models.CharField(verbose_name='Text name', max_length=256)),
                ('is_disabled', models.BooleanField(verbose_name='Is topic disabled', default=True)),
                ('is_staff_only', models.BooleanField(verbose_name='Is staff only', default=False)),
                ('is_voting_enabled', models.BooleanField(verbose_name='Is voting enabled', default=True)),
                ('truncate_at', models.IntegerField(verbose_name='Max comment number to keep', default=0)),
                ('last_updated', models.DateTimeField(verbose_name='Last updated', auto_now=True)),
                ('slug', models.SlugField(verbose_name='Topic slug')),
                ('comment_count', models.IntegerField(verbose_name='Comment count')),
                ('description', models.TextField(verbose_name='HTML description')),
                ('creator', models.ForeignKey(verbose_name='Topic creator', to=settings.AUTH_USER_MODEL)),
                ('last_comment', models.ForeignKey(to='base.Comment', verbose_name='Last comment reference', related_name='last_comment')),
                ('reply_to', models.ForeignKey(to='base.Topic', verbose_name='Reply to topic goes to', default=None, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comment',
            name='edits',
            field=models.ForeignKey(verbose_name='Edits', to='base.Edit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='moved_from',
            field=models.ForeignKey(to='base.Topic', on_delete=django.db.models.deletion.SET_DEFAULT, verbose_name='Comment moved from topic', default=None, related_name='moved_from', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='prev_comment',
            field=models.ForeignKey(to='base.Comment', on_delete=django.db.models.deletion.SET_DEFAULT, verbose_name='Answered comment', default=None, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='topic',
            field=models.ForeignKey(verbose_name='Commented in topic', to='base.Topic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(verbose_name='The commenter user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
