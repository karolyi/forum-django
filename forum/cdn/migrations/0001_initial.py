# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('orig_src', models.URLField(max_length=256, verbose_name='Original source')),
                ('mime_type', models.CharField(max_length=100, verbose_name='Mime type')),
                ('cdn_path', models.CharField(max_length=256, verbose_name='Path in CDN')),
                ('file_hash', models.CharField(max_length=200, verbose_name='File hash')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
