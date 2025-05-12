import os
import tempfile
from django.contrib import messages
from django.shortcuts import render, redirect

from analyse.marqueurs.marquers import get_kits, load_kits, save_kits
from Algo.traitement import lecture_fichier
from django.conf import settings


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