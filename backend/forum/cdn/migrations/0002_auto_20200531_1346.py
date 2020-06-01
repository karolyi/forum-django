from binascii import unhexlify

from django.db import migrations, models

from forum.utils.dbfields import Sha512Field


def imageurl_migrate_to_binhash(apps, schema_editor):
    ImageUrl = apps.get_model('forum_cdn', 'ImageUrl')
    result = list()
    for item in ImageUrl.objects.values('pk', 'src_hash'):
        result.append(
            ImageUrl(pk=item['pk'], bin_hash=unhexlify(item['src_hash'])))
    ImageUrl.objects.bulk_update(
        objs=result, fields=['bin_hash'], batch_size=500)


def image_migrate_to_binhash(apps, schema_editor):
    Image = apps.get_model('forum_cdn', 'Image')
    result = list()
    for item in Image.objects.values('pk', 'file_hash'):
        result.append(
            Image(pk=item['pk'], bin_hash=unhexlify(item['file_hash'])))
    Image.objects.bulk_update(
        objs=result, fields=['bin_hash'], batch_size=500)


class Migration(migrations.Migration):

    dependencies = [
        ('forum_cdn', '0001_initial'),
    ]

    operations = [
        # ImageUrl
        migrations.AddField(
            model_name='imageurl', name='bin_hash',
            field=Sha512Field(
                max_length=64, verbose_name='SHA512 hash of orig_src'),
            preserve_default=False,
        ),
        migrations.RunPython(code=imageurl_migrate_to_binhash, elidable=True),
        migrations.RemoveField(model_name='imageurl', name='src_hash'),
        migrations.RenameField(
            model_name='imageurl', old_name='bin_hash', new_name='src_hash'),
        migrations.AddConstraint(
            model_name='imageurl', constraint=models.UniqueConstraint(
                fields=('src_hash',), name='srchash'),
        ),
        # Image
        migrations.AddField(
            model_name='image', name='bin_hash',
            field=Sha512Field(
                max_length=64, verbose_name='File SHA512 hash'),
            preserve_default=False,
        ),
        migrations.RunPython(code=image_migrate_to_binhash, elidable=True),
        migrations.RemoveField(model_name='image', name='file_hash'),
        migrations.RenameField(
            model_name='image', old_name='bin_hash', new_name='file_hash'),
        migrations.AddConstraint(
            model_name='image', constraint=models.UniqueConstraint(
                fields=('file_hash',), name='filehash'),
        ),
    ]
