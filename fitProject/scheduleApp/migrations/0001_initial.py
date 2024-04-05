# Generated by Django 5.0.3 on 2024-04-05 12:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('client', 'Клиент'), ('admin', 'Администратор')], default='client', max_length=7)),
                ('is_client', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'profiles',
            },
        ),
        migrations.CreateModel(
            name='Gym',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('clients', models.ManyToManyField(limit_choices_to={'is_client': True}, related_name='gyms', to='scheduleApp.profile')),
            ],
            options={
                'db_table': 'gyms',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('monday', 'Понедельник'), ('tuesday', 'Вторник'), ('wednesday', 'Среда'), ('thursday', 'Четверг'), ('friday', 'Пятница'), ('saturday', 'Суббота'), ('sunday', 'Воскресенье')], max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_busy', models.BooleanField(default=False)),
                ('gym', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduleApp.gym')),
            ],
            options={
                'db_table': 'schedules',
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_busy', models.BooleanField(default=False)),
                ('client', models.ForeignKey(limit_choices_to={'is_client': True}, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='scheduleApp.profile')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduleApp.schedule')),
            ],
            options={
                'db_table': 'bookings',
            },
        ),
        migrations.CreateModel(
            name='Trainer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('gyms', models.ManyToManyField(related_name='trainers_gyms', to='scheduleApp.gym')),
            ],
            options={
                'db_table': 'trainers',
            },
        ),
        migrations.AddField(
            model_name='schedule',
            name='trainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduleApp.trainer'),
        ),
    ]