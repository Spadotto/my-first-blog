# Generated by Django 2.2.24 on 2021-07-16 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20210715_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='attachment',
            field=models.FileField(blank=True, default=None, upload_to='attachments'),
        ),
        migrations.AlterField(
            model_name='post',
            name='cover',
            field=models.ImageField(blank=True, default=None, upload_to='images'),
        ),
    ]
