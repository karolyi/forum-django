# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0001_initial'),
        ('cdn', '0012_image_global_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='project_backers',
            field=models.ManyToManyField(to='crowdfunding.ProjectBacker', verbose_name='In project backer message'),
        ),
        migrations.AddField(
            model_name='image',
            name='projects',
            field=models.ManyToManyField(to='crowdfunding.Project', verbose_name='In project'),
        ),
    ]
