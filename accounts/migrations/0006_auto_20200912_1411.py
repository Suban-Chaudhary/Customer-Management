# Generated by Django 3.0.5 on 2020-09-12 08:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20200912_1405'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='name',
            new_name='tag_name',
        ),
    ]
