# Generated by Django 4.0.1 on 2022-01-23 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shaarpy', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='links',
            options={'ordering': ['-sticky', '-date_created'], 'verbose_name_plural': 'Links'},
        ),
        migrations.AddField(
            model_name='links',
            name='sticky',
            field=models.BooleanField(default=False),
        ),
    ]
