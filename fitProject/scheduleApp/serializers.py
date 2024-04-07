from datetime import datetime, date, timedelta

from rest_framework import serializers
from .models import Trainer, Profile, Gym, Schedule, Booking


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'user', 'role')


class GymSerializer(serializers.ModelSerializer):
    clients = serializers.StringRelatedField(many=True)

    class Meta:
        model = Gym
        fields = ('name', 'address', 'description', 'clients')


class TrainerSerializer(serializers.ModelSerializer):
    gyms = GymSerializer(many=True, read_only=True)  # Nested serializer for related gyms

    class Meta:
        model = Trainer
        fields = ('id', 'first_name', 'last_name', 'surname', 'email',
                  'gyms')


class ScheduleSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    gym_name = serializers.SerializerMethodField()
    busy_times = serializers.SerializerMethodField()
    free_times = serializers.SerializerMethodField()
    gym = serializers.PrimaryKeyRelatedField(queryset=Gym.objects.all())
    trainer = serializers.PrimaryKeyRelatedField(queryset=Trainer.objects.all())

    class Meta:
        model = Schedule
        fields = ('id', 'trainer_name', 'trainer', 'day', 'start_time', 'end_time', 'gym_name', 'gym', 'busy_times', 'free_times')

    def validate(self, data):
        # checking if trainer can work at this gym
        trainer = data.get('trainer')
        gym = data.get('gym')
        day = data.get('day')
        start_time = data.get('start_time')

        if gym not in trainer.gyms.all():
            raise serializers.ValidationError("Тренер не может работать в выбранном спортзале.")

        # checking if trainer is free at this time
        overlapping_schedules = Schedule.objects.filter(
            trainer=trainer,
            day=day,
            start_time=start_time
        )

        if overlapping_schedules.exists():
            raise serializers.ValidationError("У тренера уже есть запланированное расписание на это время.")

        return data

    def create(self, validated_data):
        return Schedule.objects.create(**validated_data)
    def get_busy_times(self, obj):
        return [f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}" if obj.is_busy else None]

    def get_free_times(self, obj):
        start_time = datetime.combine(datetime.now().date(), obj.start_time)
        if obj.end_time:
            end_time = datetime.combine(datetime.now().date(), obj.end_time)
        else:
            end_time = start_time + timedelta(minutes=50)

        free_times = []

        while start_time < end_time:
            is_busy = Booking.objects.filter(schedule=obj, is_busy=True).exists()

            if not is_busy:
                free_times.append(start_time.strftime('%H:%M'))

            start_time += timedelta(hours=1)

        return free_times

    def get_trainer_name(self, obj):
        return obj.trainer.first_name + ' ' + obj.trainer.last_name

    def get_gym_name(self, obj):
        return obj.gym.name


class BookingSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)
    client = ProfileSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'schedule', 'client')