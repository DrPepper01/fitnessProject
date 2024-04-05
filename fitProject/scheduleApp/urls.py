from django.urls import path, include
from rest_framework import routers
from .views import ProfileViewSet, TrainerViewSet, ScheduleViewSet, BookingViewSet

router = routers.DefaultRouter()
router.register('profiles', ProfileViewSet)
router.register('trainers', TrainerViewSet)
router.register('schedules', ScheduleViewSet)
router.register('bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]