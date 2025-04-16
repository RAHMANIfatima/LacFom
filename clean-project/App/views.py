import os
import tempfile
from django.contrib import messages
from django.shortcuts import render, redirect

from App.services.marquers.marquers import get_kits, load_kits, save_kits
from App.utils.lecteur_donnees import lecture_fichier
from .forms import UploadFileForm
from django.conf import settings

def index(request):
    user_name = request.user.username if request.user.is_authenticated else "Utilisateur"
    texte = f"Bienvenue {user_name}"
    version= 6.0
    return render(request, "index.html", {"texte": texte})

def changer_parametres(request):
    return render(request,"parametres/parametres.html")

def manuel_utilisation(request):
    return render(request,"manuel/manuel.html")

def importer_fichier(request):
    if request.method == "POST" and request.FILES.get("fichier"):
        fichier = request.FILES["fichier"]  # Récupère le fichier sélectionné
        if not fichier.name.endswith(".txt"):  # Vérifie que c'est bien un .txt
            messages.error(request,"Le fichier doit être un fichier au format .txt.")
            return render(request, "index.html", {"erreur": "Format invalide. Seuls les fichiers .txt sont autorisés."})
        

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

    return render(request, "index.html", {"erreur": "Veuillez importer un fichier .txt valide."})


def marquers(request):
    # Vue pour afficher les marqueurs
    return render(request, 'kits/marquers.html', {'marquers': load_kits()})


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

    return render(request, 'kits/add_kit.html')


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





def afficher_importation(request):
    contenu = request.session.pop("contenu_fichier", None)  # Récupère le contenu et le supprime après affichage
    return render(request, "analyse/identification.html", {"contenu": contenu})

def traiter_choix(request):
    samples=request.session.get("samples")
    data=request.session.get("data")
    kits=request.session.get("kits")
    # print(f"Longueur de samples2 : {len(samples)}")
    # print(f"Longueur de data2 : {len(data)}")
    
    if len(samples)==3:
        print("Présence d'un père")
        return render(request,"analyse/identification_avec_pere.html",{
                      "samples":samples,
                      "data":data,
        })
    
    print("Absence de père")
    return render(request, "analyse/identification.html", {
                      "samples":samples,
                      "data":data,
                      "kits":get_kits(),
    })
