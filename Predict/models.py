from django.db import models

class Equipment(models.Model):
    name = models.CharField(max_length=200)
    project_name = models.CharField(max_length=200, default='Unknown Project')
    fuel_type = models.CharField(
        max_length=50,
        choices=[
            ('hydro', 'Hydro'),
            ('thermal', 'Thermal'),
            ('solar', 'Solar'),
            ('wind', 'Wind'),
            ('other', 'Other'),
        ],
        default='hydro'
    )
    unit_number = models.PositiveIntegerField(null=True, blank=True)
    capacity_mw = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    commissioning_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True)  # e.g., operational, maintenance

    def __str__(self):
        unit = f' Unit {self.unit_number}' if self.unit_number else ''
        return f"{self.name}{unit} ({self.fuel_type.title()})"


class Sensor(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    sensor_type = models.CharField(max_length=100)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.sensor_type} on {self.equipment.name}"


class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value = models.FloatField()

    def __str__(self):
        return f"Data {self.value} at {self.timestamp} for {self.sensor}"


class MaintenanceEvent(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField()
    status = models.CharField(max_length=50)  # e.g., Scheduled, In Progress, Completed

    def __str__(self):
        return f"Event on {self.equipment.name} from {self.start_time} to {self.end_time}"


class Prediction(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True)
    prediction_time = models.DateTimeField()
    predicted_fault = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    model_version = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='open')  # e.g., open, closed

    # Optional fields - add if you want, remove if not ready
    severity_level = models.CharField(max_length=20, blank=True, null=True)
    recommended_action = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.predicted_fault} on {self.equipment.name} at {self.prediction_time}"


# If you do want Alert or SensorFeature, define them here before importing them in admin.py
# Otherwise do NOT include them in admin or imports
from django.db import models

class Alert(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, null=True, blank=True)
    alert_time = models.DateTimeField(auto_now_add=True)
    alert_type = models.CharField(max_length=100, default=1)
    severity = models.CharField(max_length=50, blank=True)
    acknowledged = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.alert_type} alert for Prediction #{self.prediction_id} at {self.alert_time}"
