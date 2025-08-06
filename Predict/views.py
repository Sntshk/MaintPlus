from django.shortcuts import render, get_object_or_404
import json
from django.db.models import Count, Sum
from .models import Equipment, Sensor, SensorData, Prediction, MaintenanceEvent
from datetime import timedelta
import numpy as np

# Dashboard/Homepage view
def index(request):
    equipments = Equipment.objects.all().order_by('name')
    selected_equipment_id = request.GET.get('equipment')
    selected_sensor_id = request.GET.get('sensor')

    sensors = Sensor.objects.filter(equipment_id=selected_equipment_id) if selected_equipment_id else []

    sensor_data_list = []
    if selected_sensor_id:
        sensor_qs = SensorData.objects.filter(sensor_id=selected_sensor_id).order_by('timestamp')
        sensor_data_list = [
            {
                'timestamp': sd.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'value': sd.value
            }
            for sd in sensor_qs
        ]

    # Statistics for the dashboard
    equipment_count = equipments.count()
    sensor_data_count = SensorData.objects.count()
    prediction_count = Prediction.objects.count()

    # Data for pie chart: Equipment count by fuel type
    eq_type_data = Equipment.objects.values('fuel_type').annotate(count=Count('id'))
    eq_types = [entry['fuel_type'].title() for entry in eq_type_data]
    eq_type_counts = [entry['count'] for entry in eq_type_data]

    # Data for bar chart: Total capacity (MW) by fuel type
    capacity_data = Equipment.objects.values('fuel_type') \
                                 .annotate(total_capacity=Sum('capacity_mw')) \
                                 .order_by('-total_capacity')
    
    capacity_labels = [entry['fuel_type'].title() for entry in capacity_data]
    capacity_totals = [entry['total_capacity'] or 0 for entry in capacity_data]

    context = {
        'equipments': equipments,
        'sensors': sensors,
        'selected_equipment_id': int(selected_equipment_id) if selected_equipment_id else '',
        'selected_sensor_id': int(selected_sensor_id) if selected_sensor_id else '',
        'sensor_data_json': json.dumps(sensor_data_list),
        'equipment_count': equipment_count,
        'sensor_data_count': sensor_data_count,
        'prediction_count': prediction_count,
        'eq_types_json': json.dumps(eq_types),
        'eq_type_counts_json': json.dumps(eq_type_counts),
        'capacity_labels_json': json.dumps(capacity_labels),
        'capacity_totals_json': json.dumps(capacity_totals),
    }
    return render(request, 'Predict/index.html', context)

# Equipment views
def equipment_list(request):
    equipments = Equipment.objects.annotate(sensor_count=Count('sensor', distinct=True)).order_by('name')
    return render(request, 'Predict/equipment_list.html', {'equipments': equipments})

def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    sensors = equipment.sensor_set.all()
    return render(request, 'Predict/equipment_detail.html', {'equipment': equipment, 'sensors': sensors})

# Sensor views
def sensor_list(request):
    sensors = Sensor.objects.all().order_by('equipment__name', 'sensor_type')
    return render(request, 'Predict/sensor_list.html', {'sensors': sensors})

def sensor_detail(request, pk):
    sensor = get_object_or_404(Sensor, pk=pk)
    sensor_data = sensor.sensordata_set.order_by('-timestamp')[:50]
    return render(request, 'Predict/sensor_detail.html', {'sensor': sensor, 'sensor_data': sensor_data})

# Maintenance Event views
def maintenance_event_list(request):
    events = MaintenanceEvent.objects.all().order_by('-start_time')[:50]
    return render(request, 'Predict/maintenance_event_list.html', {'events': events})

def maintenance_event_detail(request, pk):
    event = get_object_or_404(MaintenanceEvent, pk=pk)
    return render(request, 'Predict/maintenance_event_detail.html', {'event': event})

# Sensor data quick listing
def sensor_data_list(request):
    sensor_data = SensorData.objects.order_by('-timestamp')[:50]
    return render(request, 'Predict/sensor_data_list.html', {'sensor_data': sensor_data})

# Predictions quick listing
def prediction_list(request):
    predictions = Prediction.objects.order_by('-prediction_time')[:50]
    return render(request, 'Predict/prediction_list.html', {'predictions': predictions})

# Sensor Trend & Forecast with thresholds and excursion detection
def sensor_trend_forecast(request):
    equipments = Equipment.objects.all().order_by('name')
    selected_equipment_id = request.GET.get('equipment')
    selected_sensor_id = request.GET.get('sensor')

    sensors = Sensor.objects.filter(equipment_id=selected_equipment_id) if selected_equipment_id else []
    historical = []
    forecast = []
    lower_threshold = None
    upper_threshold = None
    excursions = []

    if selected_sensor_id:
        try:
            sensor_obj = Sensor.objects.get(id=selected_sensor_id)
            lower_threshold = sensor_obj.min_value
            upper_threshold = sensor_obj.max_value
        except Sensor.DoesNotExist:
            sensor_obj = None

        sensor_qs = SensorData.objects.filter(sensor_id=selected_sensor_id).order_by('timestamp')
        historical = [
            {'timestamp': sd.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'value': sd.value}
            for sd in sensor_qs
        ]

        if len(historical) >= 2:
            values = np.array([d['value'] for d in historical])
            xs = np.arange(len(values))
            fit = np.polyfit(xs, values, 1)
            last_idx = len(values) - 1
            next_xs = np.arange(last_idx + 1, last_idx + 11)
            forecast_vals = fit[0] * next_xs + fit[1]
            last_date = sensor_qs.last().timestamp
            forecast = [
                {
                    'timestamp': (last_date + timedelta(days=i+1)).strftime('%Y-%m-%d %H:%M:%S'),
                    'value': float(v)
                }
                for i, v in enumerate(forecast_vals)
            ]

        for dp in historical:
            if lower_threshold is not None and dp['value'] < lower_threshold:
                excursions.append({'type': 'LOW', 'timestamp': dp['timestamp'], 'value': dp['value']})
            if upper_threshold is not None and dp['value'] > upper_threshold:
                excursions.append({'type': 'HIGH', 'timestamp': dp['timestamp'], 'value': dp['value']})
        for dp in forecast:
            if lower_threshold is not None and dp['value'] < lower_threshold:
                excursions.append({'type': 'LOW', 'timestamp': dp['timestamp'], 'value': dp['value']})
            if upper_threshold is not None and dp['value'] > upper_threshold:
                excursions.append({'type': 'HIGH', 'timestamp': dp['timestamp'], 'value': dp['value']})

    context = {
        'equipments': equipments,
        'sensors': sensors,
        'selected_equipment_id': int(selected_equipment_id) if selected_equipment_id else '',
        'selected_sensor_id': int(selected_sensor_id) if selected_sensor_id else '',
        'historical': historical,
        'forecast': forecast,
        'lower_threshold': lower_threshold,
        'upper_threshold': upper_threshold,
        'excursions': excursions,
    }
    return render(request, 'Predict/sensor_forecast.html', context)