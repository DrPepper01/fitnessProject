from django.urls import path, include
from rest_framework import routers
from .views import ProfileViewSet, TrainerViewSet, ScheduleViewSet, BookingViewSet, GymViewSet

router = routers.DefaultRouter()
router.register('profiles', ProfileViewSet)
router.register('trainers', TrainerViewSet)
router.register('schedules', ScheduleViewSet)
router.register('bookings', BookingViewSet)
router.register('gyms', GymViewSet)

urlpatterns = [
    path('', include(router.urls)),
]