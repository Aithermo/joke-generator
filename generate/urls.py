from django.urls import path, include
from . import views

urlpatterns = [
    path('joke/', views.joke_home, name='joke'),
    path("generate-joke/", views.generate, name="generate-joke"),
    path('generate_from_image/', views.generate_from_image, name='generate_from_image'),
]
