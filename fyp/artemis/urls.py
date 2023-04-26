from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('medical-history/', views.MedicalHistoryView.as_view(), name='medical_history'),
    path('dependents/', views.DependentsView.as_view(), name='dependents'),
    path('dependents/<int:pk>/', views.DependentDetailsView.as_view(), name='dependent_details'),
    path('users/', views.UsersView.as_view(), name='users'),
    path('users/<int:pk>/', views.UserDetailsView.as_view(), name='user_details'),
    path('feeding-schedule/', views.FeedingScheduleView.as_view(), name='feeding_schedule'),
    path('saved-sounds/', views.upload_sound, name='saved_sounds'),
    path('potential-emergencies/', views.PotentialEmergencyView.as_view(), name='potential_emergencies'),
    path('sensor-data/', views.SensorDataView.as_view(), name='sensor_data'),
    path('success/', views.success, name='success'),
    path('download/<str:sound_id>/', views.download_sound, name='download_sound'),
                  # Add this line
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)