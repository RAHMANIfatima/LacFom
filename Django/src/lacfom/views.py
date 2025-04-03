from django.shortcuts import render,redirect
from django.core.files.storage import default_storage

def index(request):
    user_name = request.user.username if request.user.is_authenticated else "Utilisateur"
    texte = f"Bienvenue {user_name}"
    version= 6.0
    return render(request, "lacfom/index.html", {"texte": texte})

def importer_fichier(request):
    print("\nCoucou\n")
    if request.method == "POST" and request.FILES.get("fichier"):
        fichier = request.FILES["fichier"]  # Récupère le fichier sélectionné
        if fichier.name.endswith(".txt"):  # Vérifie que c'est bien un .txt
            chemin_fichier = default_storage.save(f"uploads/{fichier.name}", fichier)
            with default_storage.open(chemin_fichier, "r") as f:
                contenu = f.read()  # Lit le contenu du fichier
            
            request.session["contenu_fichier"]=contenu
            print("ça marche")
            return redirect("importation")
        else:
            print("ça marche pas")
            return render(request, "lacfom/index.html", {"erreur": "Format invalide. Seuls les fichiers .txt sont autorisés."})
    print("Why ?")
    return render(request, "lacfom/index.html", {"erreur": "Veuillez importer un fichier .txt valide."})


def afficher_importation(request):
    contenu = request.session.pop("contenu_fichier", None)  # Récupère le contenu et le supprime après affichage
    return render(request, "lacfom/importation.html", {"contenu": contenu})

def manuel_utilisation(request):
    return render(request,"lacfom/manuel.html")

def changer_parametres(request):
    return render(request,"lacfom/parametres.html")