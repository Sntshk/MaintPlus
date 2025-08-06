from django.contrib import admin
from .models import Equipment, Sensor, SensorData, MaintenanceEvent, Prediction, Alert

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_name', 'fuel_type', 'unit_number', 'capacity_mw', 'location', 'status')
    search_fields = ('name', 'project_name', 'fuel_type', 'location')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'sensor_type', 'min_value', 'max_value')
    list_filter = ('sensor_type',)
    search_fields = ('equipment__name',)


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'timestamp', 'value')
    list_filter = ('sensor__sensor_type',)
    search_fields = ('sensor__equipment__name',)
    date_hierarchy = 'timestamp'


@admin.register(MaintenanceEvent)
class MaintenanceEventAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'start_time', 'end_time', 'status')
    list_filter = ('status',)
    search_fields = ('equipment__name', 'description')
    date_hierarchy = 'start_time'


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'sensor', 'prediction_time', 'predicted_fault', 'confidence_score', 'status')
    list_filter = ('status',)
    search_fields = ('equipment__name', 'predicted_fault')
    date_hierarchy = 'prediction_time'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'alert_time', 'severity', 'acknowledged')
    list_filter = ('alert_type', 'severity', 'acknowledged')
    date_hierarchy = 'alert_time'