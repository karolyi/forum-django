# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_cdn', '0014_auto_20151018_1044'),
        ('forum_crowdfunding', '0002_project_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='images',
            field=models.ManyToManyField(to='forum_cdn.Image', verbose_name='Images in this project description'),
        ),
        migrations.AddField(
            model_name='projectbacker',
            name='images',
            field=models.ManyToManyField(to='forum_cdn.Image', verbose_name="Images in this backer's message"),
        ),
    ]
