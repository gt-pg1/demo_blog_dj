# Generated by Django 4.2 on 2023-05-08 14:10

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='text',
            field=tinymce.models.HTMLField(max_length=2000),
        ),
    ]