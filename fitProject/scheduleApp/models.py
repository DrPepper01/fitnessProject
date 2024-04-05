from django.contrib.auth.models import User
from django.db import models

# Create your models here.

USER_ROLES = (
    ('client', 'Клиент'),
    ('admin', 'Администратор'),
)

WEEKDAYS = (
    ('monday', 'Понедельник'),
    ('tuesday', 'Вторник'),
    ('wednesday', 'Среда'),
    ('thursday', 'Четверг'),
    ('friday', 'Пятница'),
    ('saturday', 'Суббота'),
    ('sunday', 'Воскресенье'),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(choices=USER_ROLES, max_length=7, default='client')
    is_client = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.first_name} - {self.role}'

    class Meta:
        db_table = 'profiles'


class Gym(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField()
    clients = models.ManyToManyField(Profile, related_name="gyms", limit_choices_to={'is_client': True})

    def __str__(self):
        return f'{self.name}'

    def trainers(self):
        # Возвращает QuerySet тренеров, которые работают в данном фитнес-центре
        return Trainer.objects.filter(gyms=self)

    class Meta:
        db_table = 'gyms'


class Trainer(models.Model):
    # username = models.CharField(max_length=255)  # Username for login
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    gyms = models.ManyToManyField(Gym, related_name="trainers_gyms")

    def __str__(self):
        return f'{self.first_name} - Trainer'

    class Meta:
        db_table = 'trainers'


class Schedule(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    day = models.CharField(choices=WEEKDAYS, max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    is_busy = models.BooleanField(default=False)

    def get_busy_intervals(self):
        """
        Возвращает список интервалов времени, на которые уже есть бронирования,
        и отмечает их как занятые.
        """
        bookings = Booking.objects.filter(schedule=self).order_by('time')
        busy_intervals = []
        for booking in bookings:
            if booking.is_busy:
                busy_intervals.append(f"{booking.time.strftime('%H:%M')} - занято")
            else:
                busy_intervals.append(f"{booking.time.strftime('%H:%M')} - свободно")
        return busy_intervals

    def __str__(self):
        return f'{self.trainer} - {self.gym} - {self.day} - {self.start_time}'

    class Meta:
        db_table = 'schedules'

class Booking(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="bookings", limit_choices_to={'is_client': True})
    is_busy = models.BooleanField(default=False)  # По умолчанию запись не занята

    def __str__(self):
        status = "Занято" if self.is_busy else "Свободно"
        return f'{self.schedule} - ({status})'

    class Meta:
        db_table = 'bookings'

