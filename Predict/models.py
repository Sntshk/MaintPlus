from django.db import models
from django.contrib.auth.models import User

class Equipment(models.Model):
    name = models.CharField(max_length=200)
    project_name = models.CharField(max_length=200, default='Unknown Project')  # Ensure default for migration
    
    fuel_type = models.CharField(
        max_length=50,
        choices=[
            ('hydro', 'Hydro'),
            ('thermal', 'Thermal'),
            ('solar', 'Solar'),
            ('wind', 'Wind'),
            ('other', 'Other'),
        ],
        default='hydro'   # <-- Default here, *outside* the choices list
    )

    # Your other fields here...
    unit_number = models.PositiveIntegerField(null=True, blank=True)  # e.g., 1, 2, etc.
    capacity_mw = models.FloatField(null=True, blank=True)            # Unit capacity
    location = models.CharField(max_length=200, blank=True)
    commissioning_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True)              # e.g., operational, under construction

    def __str__(self):
        unit = f' Unit {self.unit_number}' if self.unit_number else ''
        return f"{self.name}{unit} ({self.fuel_type.title()})"


class Sensor(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    sensor_type = models.CharField(max_length=50)
    unit = models.CharField(max_length=10)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)

class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value = models.FloatField()

class SensorFeature(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    feature_type = models.CharField(max_length=50)
    feature_value = models.FloatField()

class MaintenanceEvent(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    event_type = models.CharField(max_length=50)
    description = models.TextField()
    fault_code = models.CharField(max_length=20, null=True, blank=True)

class Prediction(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True)
    prediction_time = models.DateTimeField()
    predicted_fault = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    model_version = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='open')

class Alert(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    alert_time = models.DateTimeField()
    severity = models.CharField(max_length=20)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    feedback = models.TextField(null=True, blank=True)

# Create your models here.
