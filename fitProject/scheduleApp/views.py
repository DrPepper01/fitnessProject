from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Profile, Trainer, Schedule, Booking, Gym
from .serializers import ProfileSerializer, TrainerSerializer, ScheduleSerializer, BookingSerializer, GymSerializer

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class GymViewSet(viewsets.ModelViewSet):
    queryset = Gym.objects.all()
    serializer_class = GymSerializer


class TrainerViewSet(viewsets.ModelViewSet):
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer

    def get_queryset(self):
        """
        Переопределяет начальный queryset, добавляя возможность фильтрации по first_name и last_name.
        """
        queryset = self.queryset  # Исходный queryset
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)

        # Фильтрация, если указаны параметры first_name или last_name

        try:
            if first_name:
                queryset = queryset.filter(first_name__icontains=first_name)
            if last_name:
                queryset = queryset.filter(last_name__icontains=last_name)

        except Trainer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Trainer not found'})

        return queryset


show_free_parameter = openapi.Parameter('show_free', openapi.IN_QUERY,
                                        description="Фильтр для отображения только свободного времени: 'true' или 'false'",
                                        type=openapi.TYPE_STRING, enum=['true', 'false'])


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        trainer_id = self.request.query_params.get('trainer_id')
        show_free = self.request.query_params.get('show_free', 'false').lower() == 'true'

        if trainer_id is not None:
            queryset = queryset.filter(trainer__id=trainer_id)

        if show_free:
            # Получаем все расписания, у которых есть бронирования, помеченные как занятые
            busy_schedules = Booking.objects.filter(
                is_busy=True
            ).values_list('schedule', flat=True)

            # Фильтруем queryset, исключая расписания, которые присутствуют в busy_schedules
            queryset = queryset.exclude(id__in=busy_schedules)

        return queryset

    @swagger_auto_schema(manual_parameters=[show_free_parameter])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=request.data['schedule'])
        client_id = request.data.get('client')

        user = request.user
        try:
            client = Profile.objects.get(pk=client_id)
        except Profile.DoesNotExist:
            # Если пользователя с таким ID нет, возвращаем ошибку
            return Response({"detail": "Пользователь с указанным ID не найден."}, status=status.HTTP_404_NOT_FOUND)

        if not client.is_client:  # Предполагается, что у вас есть такая проверка в модели пользователя
            return Response(
                {"detail": "Только клиенты могут записываться на тренировки."},
                status=status.HTTP_403_FORBIDDEN
            )

        if Booking.objects.filter(schedule=schedule).exists():
            return Response({"detail": "Это расписание уже занято."}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(
            schedule=schedule,
            client=client,
        )

        serializer = BookingSerializer(booking, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = Booking.objects.all()
        client_id = self.request.query_params.get('client_id')
        if client_id is not None:
            queryset = queryset.filter(client__id=client_id)
        return queryset

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        gym_id = self.request.GET.get('gym_id')
        form.fields['schedule'].queryset = Schedule.objects.filter(gym_id=gym_id)
        return form
