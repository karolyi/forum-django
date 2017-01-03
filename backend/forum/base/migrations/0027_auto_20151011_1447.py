# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_base', '0026_auto_20151011_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentBookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('last_updated_at', models.DateTimeField(verbose_name='Last updated at', auto_now=True)),
                ('comment', models.ForeignKey(verbose_name='Comment', to='forum_base.Comment')),
                ('topic', models.ForeignKey(verbose_name='Topic', to='forum_base.Topic')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Comment bookmark',
                'verbose_name_plural': 'Comment bookmarks',
            },
        ),
        migrations.AlterUniqueTogether(
            name='commentbookmark',
            unique_together=set([('user', 'topic')]),
        ),
    ]
