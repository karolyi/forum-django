# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_extensions.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_auto_20151009_2218'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Name')),
                ('place', models.CharField(max_length=100, verbose_name='Place')),
                ('slug', django_extensions.db.fields.AutoSlugField(max_length=100, unique=True, verbose_name='Slug', populate_from=('name',), editable=False, blank=True)),
                ('date_start', models.DateField(verbose_name='Start date')),
                ('date_end', models.DateField(verbose_name='End date')),
                ('is_enabled', models.BooleanField(default=False)),
                ('content_html', models.TextField(verbose_name='HTML content')),
                ('content_md', models.TextField(verbose_name='Markdown content')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
                ('topic', models.ForeignKey(to='base.Topic', verbose_name='Related topic', null=True)),
            ],
            options={
                'verbose_name_plural': 'Events',
                'verbose_name': 'Event',
            },
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('response', models.PositiveSmallIntegerField(choices=[(0, 'Unanswered'), (1, 'Going'), (2, 'Maybe going'), (3, 'Not going'), (4, 'Ignored')], default=0, verbose_name='Response')),
                ('event', models.ForeignKey(to='event.Event', verbose_name='Event')),
                ('invitee', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Invitee', related_name='event_responses')),
                ('inviter', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='event_sharings', verbose_name='Inviter', null=True)),
            ],
            options={
                'verbose_name_plural': 'Event Invitations',
                'verbose_name': 'Event invitation',
            },
        ),
        migrations.AlterUniqueTogether(
            name='response',
            unique_together=set([('event', 'invitee')]),
        ),
    ]
