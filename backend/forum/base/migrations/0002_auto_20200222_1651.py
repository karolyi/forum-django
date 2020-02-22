# Generated by Django 2.2.10 on 2020-02-22 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_base', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-time',), 'verbose_name': 'Comment', 'verbose_name_plural': 'Comments'},
        ),
        migrations.AlterModelOptions(
            name='introductionmodification',
            options={'verbose_name': 'Introduction modification', 'verbose_name_plural': 'Introduction modifications'},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ['-last_comment__time', 'name_text'], 'verbose_name': 'Topic', 'verbose_name_plural': 'Topics'},
        ),
        migrations.AlterIndexTogether(
            name='comment',
            index_together=set(),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['topic', 'time'], name='topic-time'),
        ),
    ]
