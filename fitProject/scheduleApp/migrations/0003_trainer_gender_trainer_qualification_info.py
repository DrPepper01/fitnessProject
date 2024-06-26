# Generated by Django 5.0.4 on 2024-04-07 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduleApp', '0002_alter_schedule_end_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainer',
            name='gender',
            field=models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский')], default='male', max_length=7),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trainer',
            name='qualification_info',
            field=models.TextField(blank=True, null=True),
        ),
    ]
