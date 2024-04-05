from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking, Schedule


# Сигнал, который
# обрабатывает создание бронирования
@receiver(post_save, sender=Booking)
def booking_created(sender, instance, created, **kwargs):
    if created:
        instance.schedule.is_busy = True
        instance.schedule.save()
        instance.is_busy = True
        instance.save()
    print('\n')
    print('Signal is worked on CREATED !!!!!!!!')


# Сигнал, который обрабатывает удаление бронирования
@receiver(post_delete, sender=Booking)
def booking_deleted(sender, instance, **kwargs):
    # Проверка, остались ли другие бронирования на это же расписание
    if not Booking.objects.filter(schedule=instance.schedule).exists():
        instance.schedule.is_busy = False
        instance.schedule.save()
    print('\n')
    print('Signal is worked on DELETED !!!!!!!!')