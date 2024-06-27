from django.urls import path
from . import views

urlpatterns = [
    path('meme/', views.meme_input, name='meme'),  # URL for meme input form
    path("meme/generate_meme/", views.generate_meme, name="generate_meme"),  # URL for meme generation
]
