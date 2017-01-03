# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_crowdfunding', '0001_initial'),
        ('forum_cdn', '0012_image_global_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='project_backers',
            field=models.ManyToManyField(to='forum_crowdfunding.ProjectBacker', verbose_name='In project backer message'),
        ),
        migrations.AddField(
            model_name='image',
            name='projects',
            field=models.ManyToManyField(to='forum_crowdfunding.Project', verbose_name='In project'),
        ),
    ]
