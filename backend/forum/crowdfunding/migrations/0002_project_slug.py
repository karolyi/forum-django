# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_crowdfunding', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(blank=True, populate_from=('name',), verbose_name='Slug', unique=True, editable=False),
        ),
    ]
