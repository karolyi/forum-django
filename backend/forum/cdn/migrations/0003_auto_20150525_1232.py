# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models, transaction


def migrate_forward(apps, schema_editor):
    """
    Migrates the orig_src field from Image to ImageUrl table
    """
    Image = apps.get_model('forum_cdn', 'Image')
    ImageUrl = apps.get_model('forum_cdn', 'ImageUrl')
    bulk_list = []
    counter = 0
    for image in Image.objects.all():
        bulk_list.append(
            ImageUrl(
                image=image,
                orig_src=image.orig_src
            ))
        if image.id > counter + 1000:
            counter = image.id
            ImageUrl.objects.bulk_create(bulk_list)
            bulk_list.clear()
    ImageUrl.objects.bulk_create(bulk_list)


def migrate_backward(apps, schema_editor):
    """
    Migrates the orig_src field from ImageUrl to Image table
    """
    ImageUrl = apps.get_model('forum_cdn', 'ImageUrl')
    Image = apps.get_model('forum_cdn', 'Image')
    with transaction.atomic():
        for image_url in ImageUrl.objects.all().order_by('id'):
            images = Image.objects.filter(id=image_url.image_id)
            images.update(orig_src=image_url.orig_src)
        Image.objects.filter(orig_src='').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('forum_cdn', '0002_auto_20150403_2024'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageUrl',
            fields=[
                ('id', models.AutoField(
                    serialize=False, primary_key=True,
                    verbose_name='ID', auto_created=True)),
                ('orig_src', models.URLField(
                    verbose_name='Original source',
                    max_length=512)),
            ],
            options={
                'verbose_name': 'ImageUrl',
                'verbose_name_plural': 'ImageUrls',
            },
        ),
        migrations.AlterModelOptions(
            name='image',
            options={'verbose_name': 'Image', 'verbose_name_plural': 'Images'},
        ),
        migrations.AlterModelOptions(
            name='missingimage',
            options={'verbose_name': 'Missing Image',
                     'verbose_name_plural': 'Missing Images'},
        ),
        migrations.AlterField(
            model_name='image',
            name='cdn_path',
            field=models.FilePathField(
                path=settings.PATH_CDN_ROOT,
                unique=True, max_length=191, verbose_name='Path in CDN'),
        ),
        migrations.AddField(
            model_name='imageurl',
            name='image',
            field=models.ForeignKey(
                verbose_name='The CDN file', to='forum_cdn.Image')),
        migrations.RunPython(
            migrate_forward, reverse_code=migrate_backward),
        migrations.RemoveField(
            model_name='image', name='orig_src'),
    ]
