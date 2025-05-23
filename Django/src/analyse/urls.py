from django.urls import path
from .views import traiter_choix,analyse_resultat,afficher_importation,choix_kit,attribution_origine,affichage_resultat,exportation_pdf,change_radio_selection



urlpatterns = [
    path("identification/",traiter_choix,name="traiter_choix"),
    path("origine/",attribution_origine,name="attribution_origine"),
    path("analyse-resultat/",analyse_resultat,name="analyse_resultat"),
    path("affichage-resultat",affichage_resultat,name="affichage_resultat"),
    path("visualisation/",afficher_importation,name="afficher_importation"),
    path('choix-du-kit/',choix_kit,name="choix_kit"),
    path('exportation',exportation_pdf,name="exportation_pdf"),
    path('change_radio_selection/', change_radio_selection, name='change_radio_selection'),

]