from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('manuel/', views.manuel, name='manual'),
    path('marquers/', views.marquers, name='marquers'), 
    path('add-kit/', views.add_kit, name='add-kit'),
    path('delete-kit/<str:kit_name>/', views.delete_kit, name='delete-kit'),
    # ...
]
