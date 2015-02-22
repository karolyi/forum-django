# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20150222_1605'),
        ('cdn', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MissingImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('src', models.URLField(verbose_name='Original source', max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='images',
            name='comment',
            field=models.ManyToManyField(default=1, verbose_name='Found in comment', to='base.Comments', null=None),
            preserve_default=True,
        ),
    ]
