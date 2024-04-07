from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from rest_framework import viewsets
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


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=request.data['schedule'])
        user = request.user
        if user.is_authenticated:
            try:
                profile = user.profile
            except ObjectDoesNotExist:
                profile = Profile.objects.create(user=user)

        if not profile.is_client:
            return Response(
                {"detail": "Тренеру нельзя записаться к другому тренеру."},
                status=status.HTTP_403_FORBIDDEN
            )

        booking = Booking.objects.create(
            schedule=schedule,
            client=profile,
            date=request.data['date'],
            time=request.data['time'],
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
