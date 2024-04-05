from rest_framework import serializers
from .models import Trainer, Profile, Gym, Schedule, Booking


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'user', 'role')


class GymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym
        fields = ('name', 'address', 'description')  # Customize fields as needed


class TrainerSerializer(serializers.ModelSerializer):
    gyms = GymSerializer(many=True, read_only=True)  # Nested serializer for related gyms

    class Meta:
        model = Trainer
        fields = ('id', 'first_name', 'last_name', 'surname', 'email',  # Include relevant fields
                  'gyms')  # Nested serializer field


class ScheduleSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    gym_name = serializers.SerializerMethodField()
    busy_times = serializers.SerializerMethodField()
    free_times = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ('id', 'trainer_name', 'day', 'start_time', 'end_time', 'gym_name', 'busy_times', 'free_times')

    # def get_is_busy(self, obj):
    #     """
    #             Возвращает список интервалов времени, на которые уже есть бронирования,
    #             и отмечает их как занятые.
    #             """
    #     bookings = Booking.objects.filter(schedule=obj).order_by('time')
    #     busy_intervals = []
    #     for booking in bookings:
    #         if booking.is_busy:
    #             busy_intervals.append(f"{booking.time.strftime('%H:%M')} - занято")
    #         else:
    #             busy_intervals.append(f"{booking.time.strftime('%H:%M')} - свободно")
    #     return busy_intervals

    def get_busy_times(self, obj):
        bookings = Booking.objects.filter(schedule=obj)
        return [f"{booking.time.strftime('%H:%M')}" for booking in bookings if booking.is_busy]

    def get_free_times(self, schedule_id):
        # Получаем объект Schedule по его уникальному идентификатору
        schedule = Schedule.objects.get(pk=schedule_id)

        # Получаем все бронирования для данного расписания
        bookings = Booking.objects.filter(schedule=schedule)

        # Создаем список свободного времени, начинающийся с начального времени расписания
        free_times = [schedule.start_time]

        # Проходим по всем бронированиям и ищем свободные интервалы между ними
        for booking in bookings:
            if not booking.is_busy:
                # Если бронирование свободное, добавляем его начальное и конечное время в список свободного времени
                free_times.append(booking.schedule.start_time)
                free_times.append(booking.schedule.end_time)

        # Добавляем конечное время расписания в список свободного времени
        free_times.append(schedule.end_time)

        # Преобразуем время в формат строк и возвращаем список свободного времени
        free_times = [time.strftime('%H:%M') for time in free_times]
        return free_times

    def get_trainer_name(self, obj):
        return obj.trainer.first_name + ' ' + obj.trainer.last_name  # или obj.trainer.first_name + ' ' + obj.trainer.last_name, если у вас есть эти поля в модели Trainer

    def get_gym_name(self, obj):
        return obj.gym.name


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('id', 'schedule', 'client', 'date', 'time')