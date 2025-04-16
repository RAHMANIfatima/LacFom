from django.urls import path, include

from App.Views.kits_views import add_kit, delete_kit, marquers
from App.views import changer_parametres, importer_fichier, index, manuel_utilisation, traiter_choix

urlpatterns = [
    path('',index, name='index'),
    path("importer/",importer_fichier,name="importer_fichier"),
    path('parametres/',changer_parametres,name='changer_parametres'),
    path('marquers/', marquers, name='marquers'), 
    path('manuel-d-utilisation/',manuel_utilisation,name='manuel_utilisation'),
    path('add-kit/', add_kit, name='add-kit'),
    path('delete-kit/<str:kit_name>/', delete_kit, name='delete-kit'),
    path("analyse/identification/",traiter_choix,name="traiter_choix"),
    # ...
]