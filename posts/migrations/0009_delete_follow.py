# Generated by Django 2.2.9 on 2021-04-11 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_follow'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Follow',
        ),
    ]
