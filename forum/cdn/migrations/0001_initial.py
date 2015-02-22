# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('orig_src', models.URLField(verbose_name='Original source', max_length=256)),
                ('mime_type', models.CharField(verbose_name='Mime type', max_length=100)),
                ('cdn_path', models.CharField(verbose_name='Path in CDN', max_length=256)),
                ('file_hash', models.CharField(verbose_name='File hash', max_length=200)),
                ('comment', models.ManyToManyField(verbose_name='Found in comment', to='base.Comment', default=1, null=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MissingImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('src', models.URLField(verbose_name='Original source', max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
