from django.urls import path
from .views import home, generate, generate_api

urlpatterns = [
    path('', home, name='home'),
    path('generate/', generate, name='generate'),
    path('api/generate/', generate_api, name='generate_api'),  # New API endpoint
]
