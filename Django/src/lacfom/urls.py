"""lacfom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from .views import index,importer_fichier,manuel_utilisation,changer_parametres

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',index, name='index'),
    path('analyse/',include("analyse.urls")),
    path('admin/', admin.site.urls),
    path("importer/",importer_fichier,name="importer_fichier"),
    # path("importation/",afficher_importation,name="importation"),
    path('manuel-d-utilisation/',manuel_utilisation,name='manuel_utilisation'),
    path('parametres/',changer_parametres,name='changer_parametres'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Permet de stocker temporairement les fichiers enregistrés




"""
path() doit inclure 3 arguments :
- Ce qui va definir son chemin dans l'URL
- Le nom de la fonction qui doit être appelée (views.py)
- Le nom qui va permettre d'appeler l'URL dans les fichiers HTML
"""

