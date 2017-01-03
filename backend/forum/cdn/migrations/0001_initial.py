# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('orig_src', models.URLField(
                    max_length=512, null=False,
                    verbose_name='Original source')),
                ('mime_type', models.CharField(
                    max_length=100, verbose_name='Mime type')),
                ('cdn_path', models.CharField(
                    max_length=191, unique=True, verbose_name='Path in CDN')),
                ('file_hash', models.CharField(
                    max_length=200, verbose_name='File hash')),
                ('comment', models.ManyToManyField(
                    default=1, null=False, to='forum_base.Comment',
                    verbose_name='Found in comment')),
            ],
        ),
        migrations.CreateModel(
            name='MissingImage',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('src', models.URLField(
                    db_index=True, max_length=10,
                    verbose_name='Original source')),
            ],
        ),
    ]
