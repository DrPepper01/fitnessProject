from django.urls import path, include, re_path
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import ProfileViewSet, TrainerViewSet, ScheduleViewSet, BookingViewSet, GymViewSet

schema_view = get_schema_view(
    openapi.Info(
        title='API ',
        default_version='v1',
        description='Test',
        terms_of_service='',
        contact=openapi.Contact(email=''),
        license=openapi.License(name='')
    ),
    public=True
)

router = routers.DefaultRouter()
router.register('profiles', ProfileViewSet)
router.register('trainers', TrainerViewSet)
router.register('schedules', ScheduleViewSet)
router.register('bookings', BookingViewSet)
router.register('gyms', GymViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger_ui'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),

]