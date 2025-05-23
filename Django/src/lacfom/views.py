from django.shortcuts import render,redirect
from django.contrib import messages
from Algo.traitement import lecture_fichier
from django.conf import settings
import os
import json 

def index(request):
    """
    Page d'accueil de l'application.
    """
    user_name = request.user.username if request.user.is_authenticated else "Utilisateur"
    texte = f"Bienvenue {user_name}"
    version= "6.0"

    request.session["version"]=version

    return render(request, "lacfom/index.html", {"texte": texte})

def importer_fichier(request):
    """
    Fonction qui permet d'importer le fichier.
    Vérifies que le fichier importé est bien un fichier texte, enregistres le fichier dans un dossier media/uploads et assigne le contenue du fichier aux variables samples et donnees.
    sample : liste avec nom des échantillons
    donnees :  dataframe avec l'ensemble de donnees

    Rediriges vers la page d'identification des échantillons.
    """
    if request.method == "POST" and request.FILES.get("fichier"):
        fichier = request.FILES["fichier"]  # Récupère le fichier sélectionné
        if not fichier.name.endswith(".txt"):  # Vérifie que c'est bien un .txt
            messages.error(request,"Le fichier doit être un fichier au format .txt.")
            return render(request, "lacfom/index.html", {"erreur": "Format invalide. Seuls les fichiers .txt sont autorisés."})
        

        contenu = fichier.read()  # Lit le contenu du fichier
        request.session["contenu_fichier"] = contenu.decode("utf-8")

        # Chemin à modifier avec l'arborescence des postes du CHU
        uploads_path="/home/malala/cours/lacfom/PP16/PP16-test/Patient_1"

        chemin_fichier = os.path.join(uploads_path, fichier.name)
        with open(chemin_fichier,"wb") as dest:
            dest.write(contenu)

        resultat=lecture_fichier(chemin_fichier)
            
        if isinstance(resultat,str):
            messages.error(request, f"Erreur de lecture du fichier : {resultat}")
            return redirect("index")

        samples, donnees=resultat
        request.session["chemin_fichier"]=chemin_fichier
        request.session["chemin_dossier"]=uploads_path
        request.session["samples"]=samples
        request.session["donnees"]=donnees

        # print(f"Longueur de samples : {len(samples)}")
        # print(f"Longueur de donnees : {len(donnees)}")
        # print(f"Contenu de samples : {samples}")
        # print(f"Contenu de donnees : {donnees}")


        return redirect("traiter_choix") # traiter_choix se trouve dans la partie Analyse

    return render(request, "lacfom/index.html", {"erreur": "Veuillez importer un fichier .txt valide."})


def manuel_utilisation(request):
    """
    Page avec le manuel d'utilisation de l'application.
    """
    return render(request,"lacfom/manuel.html")

def changer_parametres(request):
    """
    Page paramètres.

    Enregistre les valeurs entrées pour l'algorithme et les données du kit.
    """
    valeurs_defaut = {
        "nmarqueurs": "2",
        "hpics": "1/3",
        "emet": "PBP-P2A-GEN",
        "enti": "PBP-PTBM"
    }

    if request.method == "POST":
        next_url = request.POST.get("next")
        if "reset" in request.POST:
            # Réinitialiser les paramètres et supprimer les données du kit
            request.session["parametres"] = valeurs_defaut
            request.session.pop("kit_data", None)  # Supprimer les données du kit
            if next_url:
                return redirect(next_url)
            else:
                return redirect("index")
            
        elif "previous" in request.POST:
            # Retourner à la page précédente
            if next_url:
                return redirect(next_url)
            else:
                return redirect("index")
        else:
            # Enregistrer les nouvelles valeurs et les données du kit
            request.session["parametres"] = {
                "nmarqueurs": request.POST.get("nmarqueurs", "2"),
                "hpics": request.POST.get("hpics", "1/3"),
                "emet": request.POST.get("emet", "PBP-P2A-GEN"),
                "enti": request.POST.get("enti", "PBP-PTBM")
            }

            # Gérer les données du kit
            kit_data = request.POST.get("kit_data")
            if kit_data:
                try:
                    kit_data = json.loads(kit_data)  # Convertir en dictionnaire
                    request.session["kit_data"] = kit_data
                    messages.success(request, "Les paramètres et le kit ont été enregistrés avec succès.")
                except json.JSONDecodeError:
                    messages.error(request, "Erreur : données du kit invalides.")
            else:
                messages.success(request, "Les paramètres ont été enregistrés avec succès.")

            if next_url:
                return redirect(next_url)
            else:
                return redirect("index")

    # Récupération des paramètres depuis la session ou valeurs par défaut
    parametres = request.session.get("parametres", valeurs_defaut)

    request.session["N"] = parametres["nmarqueurs"]
    request.session["H"] = parametres["hpics"]
    request.session["emetteur"] = parametres["emet"]
    request.session["entite"] = parametres["enti"]

    return render(request, "lacfom/parametres.html", {"parametres": parametres})