# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(verbose_name='Commented at', auto_now=True)),
                ('number', models.IntegerField(verbose_name='Comment number in topic')),
                ('voting_value', models.IntegerField(verbose_name='Value of up/downvotes')),
                ('content', models.TextField(verbose_name='Content')),
                ('host', models.CharField(max_length=256, verbose_name='Host of the commenter')),
                ('ip', models.IPAddressField(verbose_name='IP of the commenter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Edits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(verbose_name='Edit timestamp', auto_now=True)),
                ('diff', models.TextField(verbose_name='Diff of the previous version')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('html', models.CharField(max_length=256, verbose_name='HTML name')),
                ('text', models.CharField(max_length=256, verbose_name='Text name')),
                ('is_disabled', models.BooleanField(verbose_name='Is topic disabled', default=True)),
                ('is_staff_only', models.BooleanField(verbose_name='Is staff only', default=False)),
                ('is_voting_enabled', models.BooleanField(verbose_name='Is voting enabled', default=True)),
                ('truncate_at', models.IntegerField(verbose_name='Max comment number to keep', default=0)),
                ('last_updated', models.DateTimeField(verbose_name='Last updated', auto_now=True)),
                ('slug', models.SlugField(verbose_name='Topic slug')),
                ('comment_count', models.IntegerField(verbose_name='Comment count')),
                ('description', models.TextField(verbose_name='HTML description')),
                ('creator', models.ForeignKey(verbose_name='Topic creator', to=settings.AUTH_USER_MODEL)),
                ('last_comment', models.ForeignKey(verbose_name='Last comment reference', to='base.Comments')),
                ('reply_to', models.ForeignKey(blank=True, to='base.Topics', default=None, verbose_name='Reply to topic goes to')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comments',
            name='edits',
            field=models.ForeignKey(verbose_name='Edits', to='base.Edits'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comments',
            name='moved_from',
            field=models.ForeignKey(related_name='moved_from', on_delete=django.db.models.deletion.SET_DEFAULT, blank=True, to='base.Topics', default=None, verbose_name='Comment moved from topic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comments',
            name='prev_comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_DEFAULT, blank=True, to='base.Comments', default=None, verbose_name='Answered comment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comments',
            name='topic',
            field=models.ForeignKey(verbose_name='Commented in topic', to='base.Topics'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comments',
            name='user',
            field=models.ForeignKey(verbose_name='The commenter user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
