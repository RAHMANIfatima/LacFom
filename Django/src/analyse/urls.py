from django.urls import path
from .views import traiter_choix

urlpatterns = [
    path("identification/",traiter_choix,name="traiter_choix"),
]