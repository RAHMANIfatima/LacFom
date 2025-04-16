from django.shortcuts import render,redirect
from django.contrib import messages
from .utils.lecteur_donnees import lecture_fichier
from django.conf import settings
import os
import tempfile
from django.http import JsonResponse  # Import JsonResponse
import json  # Ensure this is also imported if not already
from lacfom.services.marquers.marquers import load_kits, save_kits
from .forms import UploadFileForm
from django.contrib import messages



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


def marquers(request):
    # Vue pour afficher les marqueurs
    return render(request, 'lacfom/marquers/marquers.html', {'marquers': load_kits()})


def add_kit(request):
    if request.method == 'POST':
        kit_name = request.POST.get('kit_name')

        if not kit_name:
            messages.error(request, "Le nom du kit est requis.")
            return redirect('add-kit')

        kits = load_kits()
        if kit_name in kits:
            messages.error(request, "Un kit avec ce nom existe déjà.")
            return redirect('add-kit')

        # Construire les marqueurs
        markers_data = {}
        for key in request.POST:
            if key.startswith('markers['):
                marker_index = key.split('[')[1].split(']')[0]
                marker_name = request.POST.get(f'markers[{marker_index}][name]')
                marker_alleles = request.POST.get(f'markers[{marker_index}][alleles]')
                if marker_name and marker_alleles:
                    # Convertir les allèles en entiers si possible
                    alleles_list = []
                    for allele in marker_alleles.split(','):
                        allele = allele.strip()
                        try:
                            allele = int(allele)  # Conversion en entier
                        except ValueError:
                            pass  # Si la conversion échoue, garder en str
                        alleles_list.append(allele)
                    markers_data[marker_name] = alleles_list

        # Vérifier si des marqueurs ont été ajoutés
        if not markers_data:
            messages.error(request, "Au moins un marqueur est requis.")
            return redirect('add-kit')

        # Ajouter le kit
        kits[kit_name] = markers_data
        save_kits(kits)
        messages.success(request, f'Le kit "{kit_name}" a été ajouté avec succès.')
        return redirect('marquers')

    return render(request, 'lacfom/marquers/add_kit.html')


def delete_kit(request, kit_name):
    if request.method == 'POST':
        kits = load_kits()
        if kit_name in kits:
            if list(kits.keys())[0] == kit_name:  # Vérifie si c'est le premier kit
                messages.error(request, "Le premier kit ne peut pas être supprimé.")
                return redirect('marquers')
            del kits[kit_name]
            save_kits(kits)
            messages.success(request, f'Le kit "{kit_name}" a été supprimé avec succès.')
        else:
            messages.error(request, f'Le kit "{kit_name}" est introuvable.')
        return redirect('marquers')
    messages.error(request, "Méthode non autorisée.")
    return redirect('marquers')



