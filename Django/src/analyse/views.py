from django.shortcuts import render
# Create your views here.

def afficher_importation(request):
    contenu = request.session.pop("contenu_fichier", None)  # Récupère le contenu et le supprime après affichage
    return render(request, "analyse/importation.html", {"contenu": contenu})