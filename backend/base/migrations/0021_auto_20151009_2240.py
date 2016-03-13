# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_auto_20151009_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(unique=True, verbose_name='Slug', editable=False, max_length=100, populate_from=('name_text',), blank=True),
        ),
    ]
