# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0026_auto_20151011_1043'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('text', models.CharField(max_length=150, verbose_name='Text')),
                ('votes', models.PositiveIntegerField(verbose_name='Vote count')),
                ('order', models.PositiveSmallIntegerField(verbose_name='Order ID')),
            ],
            options={
                'verbose_name_plural': 'Choices',
                'verbose_name': 'Choice',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('text', models.CharField(max_length=150, verbose_name='Text')),
                ('slug', django_extensions.db.fields.AutoSlugField(blank=True, editable=False, verbose_name='Slug', unique=True, populate_from=('text',))),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('is_enabled', models.BooleanField(verbose_name='Enabled', default=False)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('topic', models.ForeignKey(null=True, to='base.Topic', verbose_name='In topic', default=None)),
            ],
            options={
                'verbose_name_plural': 'Questions',
                'verbose_name': 'Question',
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('last_modified_at', models.DateTimeField(auto_now=True, verbose_name='Last modified at')),
                ('choice', models.ForeignKey(to='poll.Choice', verbose_name='Choice')),
                ('question', models.ForeignKey(to='poll.Question', verbose_name='Question')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Votes',
                'verbose_name': 'Vote',
            },
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(to='poll.Question', verbose_name='Question'),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'question')]),
        ),
    ]
