# Generated by Django 3.2.9 on 2021-12-11 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='ProgrammeName',
            field=models.CharField(default='', max_length=150, null=True),
        ),
    ]
