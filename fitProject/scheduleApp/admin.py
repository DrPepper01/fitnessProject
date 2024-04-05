from django.contrib import admin
from .models import Gym, Trainer, Profile, Schedule, Booking
# Register your models here.

admin.site.register(Gym, )
admin.site.register(Trainer)
admin.site.register(Profile)
admin.site.register(Schedule)
admin.site.register(Booking)
