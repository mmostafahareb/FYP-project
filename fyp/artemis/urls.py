from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('lullabies/<int:i>', views.getLullaby),
    path('lullabies/', views.postLullaby),
    path('laser/',views.moveLaser),
    path('users/,<user>',views.getUser),
    path('users/',views.addUser),
    path('dependents/<dependent>',views.getDependent),
    path('dependents/',views.addDependent),
    path('dependents/<dependent>/proofing',views.generateAnalysis),
]