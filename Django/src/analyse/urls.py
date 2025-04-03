from django.urls import path
from .views import afficher_importation

urlpatterns = [
    path("importation/",afficher_importation,name="importation"),
]