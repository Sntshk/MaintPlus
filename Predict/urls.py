# Predict/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='predict_index'),
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('sensor-data/', views.sensor_data_list, name='sensor_data_list'),
    path('predictions/', views.prediction_list, name='prediction_list'),
    path('trend-forecast/', views.sensor_trend_forecast, name='sensor_trend_forecast'),
    # New URLs for sensors and maintenance events
    path('sensors/', views.sensor_list, name='sensor_list'),
    path('sensors/<int:pk>/', views.sensor_detail, name='sensor_detail'),
    path('maintenance-events/', views.maintenance_event_list, name='maintenance_event_list'),
    path('maintenance-events/<int:pk>/', views.maintenance_event_detail, name='maintenance_event_detail'),
]
