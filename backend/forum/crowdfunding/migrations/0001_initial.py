# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0026_auto_20151011_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('last_updated_at', models.DateTimeField(auto_now=True, verbose_name='Last updated at')),
                ('ends_at', models.DateTimeField(verbose_name='Ends at')),
                ('status', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Disabled'), (1, 'Running'), (2, 'Finished'), (3, 'Archived')], verbose_name='Status')),
                ('content_html', models.TextField(verbose_name='HTML content')),
                ('content_md', models.TextField(verbose_name='Markdown content')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
                ('related_topic', models.ForeignKey(default=None, null=True, verbose_name='Related topic', to='base.Topic')),
            ],
            options={
                'verbose_name_plural': 'Projects',
                'verbose_name': 'Project',
            },
        ),
        migrations.CreateModel(
            name='ProjectBacker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated_at', models.DateTimeField(auto_now=True, verbose_name='Last updated at')),
                ('content_html', models.TextField(verbose_name='HTML content')),
                ('content_md', models.TextField(verbose_name='Markdown content')),
                ('project', models.ForeignKey(to='crowdfunding.Project', verbose_name='Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Backer')),
            ],
            options={
                'verbose_name_plural': 'Project backers',
                'verbose_name': 'Project backer',
            },
        ),
        migrations.AlterUniqueTogether(
            name='projectbacker',
            unique_together=set([('project', 'user')]),
        ),
    ]
