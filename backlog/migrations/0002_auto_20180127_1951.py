# Generated by Django 2.0.1 on 2018-01-27 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backlog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backlog',
            name='start_at',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='sprint',
            name='start_at',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='end_at',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='task',
            name='start_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]