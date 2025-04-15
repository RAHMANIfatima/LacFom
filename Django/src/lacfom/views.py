from django.shortcuts import render,redirect
from django.contrib import messages
from .utils.lecteur_donnees import lecture_fichier
from django.conf import settings
import os

def index(request):
    user_name = request.user.username if request.user.is_authenticated else "Utilisateur"
    texte = f"Bienvenue {user_name}"
    version= 6.0
    return render(request, "lacfom/index.html", {"texte": texte})

def importer_fichier(request):
    if request.method == "POST" and request.FILES.get("fichier"):
        fichier = request.FILES["fichier"]  # Récupère le fichier sélectionné
        if not fichier.name.endswith(".txt"):  # Vérifie que c'est bien un .txt
            messages.error(request,"Le fichier doit être un fichier au format .txt.")
            return render(request, "lacfom/index.html", {"erreur": "Format invalide. Seuls les fichiers .txt sont autorisés."})
        

        contenu = fichier.read()  # Lit le contenu du fichier
        request.session["contenu_fichier"] = contenu.decode("utf-8")

        uploads_path = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(uploads_path, exist_ok=True)

        chemin_fichier = os.path.join(uploads_path, fichier.name)
        
        with open(chemin_fichier,"wb") as dest:
            dest.write(contenu)

        resultat=lecture_fichier(chemin_fichier)
            
        if isinstance(resultat,str):
            messages.error(request, f"Erreur de lecture du fichier : {resultat}")
            return redirect("index")

        samples, data=resultat
        request.session["samples"]=samples
        request.session["data"]=data

        # print(f"Longueur de samples : {len(samples)}")
        # print(f"Longueur de data : {len(data)}")

        return redirect("traiter_choix") # traiter_choix se trouve dans la partie Analyse

    return render(request, "lacfom/index.html", {"erreur": "Veuillez importer un fichier .txt valide."})


def manuel_utilisation(request):
    return render(request,"lacfom/manuel.html")

def changer_parametres(request):
    return render(request,"lacfom/parametres.html")