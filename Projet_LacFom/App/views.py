import os
import tempfile
from django.shortcuts import render
from .forms import UploadFileForm

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