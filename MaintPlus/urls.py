from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('predict/', include('Predict.urls')),
    path('', lambda request: redirect('predict_index')),  # redirect root to Predict app homepage
]
