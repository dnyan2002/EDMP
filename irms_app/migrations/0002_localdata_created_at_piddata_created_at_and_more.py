# Generated by Django 4.2.6 on 2025-03-27 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irms_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='localdata',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='piddata',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='connection',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
