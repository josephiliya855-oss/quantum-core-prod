from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('control/reset/', views.reset_system_state, name='reset_system'),
]
