# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_auto_20151011_1904'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='commentvote',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='commentvote',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='commentvote',
            name='user',
        ),
        migrations.DeleteModel(
            name='CommentVote',
        ),
    ]
