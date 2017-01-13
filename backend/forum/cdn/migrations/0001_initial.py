# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-13 19:25
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mime_type', models.CharField(max_length=100, verbose_name='Mime type')),
                ('cdn_path', models.FilePathField(max_length=191, path='/home/karolyi/Work/forum-django-cdn/original', unique=True, verbose_name='Path in CDN')),
                ('file_hash', models.CharField(max_length=128, unique=True, verbose_name='File SHA512 hash')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
        ),
        migrations.CreateModel(
            name='ImageUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orig_src', models.URLField(max_length=512, verbose_name='Original source')),
                ('src_hash', models.CharField(max_length=128, unique=True, verbose_name='SHA512 hash of orig_src')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_cdn.Image', verbose_name='The CDN file')),
            ],
            options={
                'verbose_name': 'ImageUrl',
                'verbose_name_plural': 'ImageUrls',
            },
        ),
        migrations.CreateModel(
            name='MissingImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.URLField(db_index=True, max_length=191, unique=True, verbose_name='Original source')),
            ],
            options={
                'verbose_name': 'Missing Image',
                'verbose_name_plural': 'Missing Images',
            },
        ),
    ]
