import os
import tempfile
from django.shortcuts import render, redirect
from django.http import JsonResponse  # Import JsonResponse
import json  # Ensure this is also imported if not already
from .services.marquers.marquers import load_kits, save_kits
from .forms import UploadFileForm
from django.contrib import messages


"""def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Sauvegarde temporaire du fichier uploadé
            uploaded_file = request.FILES['fichier']
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            # Traitement du fichier
            lecture = traitement.lecture_fichier(tmp_path)
            if isinstance(lecture, str):
                # Erreur lors de la lecture (ex : témoin absent)
                context = {'form': form, 'error': lecture}
                os.remove(tmp_path)
                return render(request, 'upload.html', context)
            else:
                samples, donnees = lecture

            # Attribution par défaut :
            if len(samples) >= 2:
                sample_dict = {"mother": samples[0], "foetus": samples[1]}
                if len(samples) >= 3:
                    sample_dict["father"] = samples[2]
            else:
                context = {'form': form, 'error': "Nombre de samples insuffisant."}
                os.remove(tmp_path)
                return render(request, 'upload.html', context)

            # Création de l’objet Echantillon
            echantillon = traitement.computedata(sample_dict, donnees)
            # Lancer la concordance et l’analyse des marqueurs
            traitement.concordance_ADN(echantillon)
            echantillon.analyse_marqueur()
            
            # Récupération des résultats
            resultat = echantillon.get_resultats()

            # Choisir la clé de conclusion selon la structure
            if "Conclusion" in resultat:
                conclusion_key = "Conclusion"
            else:
                conclusion_key = "Concordance Mere/Foetus"

            # Création d'une liste zippée pour faciliter l'affichage
            resultat_list = list(zip(resultat["Marqueur"],
                                     resultat[conclusion_key],
                                     resultat["Détails M/F"]))
            os.remove(tmp_path)
            return render(request, 'resultats.html', {'resultat_list': resultat_list})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
"""

def accueil(request):
    # Exemple de vue accueil
    return render(request, 'accueil.html', {'nom_utilisateur': 'Utilisateur'})

def manuel(request):
    # Vue pour afficher le manuel d'utilisation
    return render(request, 'manuel.html')

def marquers(request):
    # Vue pour afficher les marqueurs
    return render(request, 'marquers/marquers.html', {'marquers': load_kits()})


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

    return render(request, 'marquers/add_kit.html')


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