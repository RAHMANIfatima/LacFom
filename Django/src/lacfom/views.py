from django.shortcuts import render
from .marqueurs.marquers import get_kits, load_kits, save_kits

from Algo.echantillon import Echantillon
from Algo.individus import Individus
from Algo.foetus import Foetus
from Algo.mere import Mere
from Algo.pere import Pere
from Algo.temoin import Temoin


def afficher_importation(request):
    contenu = request.session.pop("contenu_fichier", None)  # Récupère le contenu et le supprime après affichage
    return render(request, "analyse/visualisation.html", {"contenu": contenu})

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
                      "kits":get_kits(),
        })
    
    print("Absence de père")
    return render(request, "analyse/identification.html", {
                      "samples":samples,
                      "data":data,
                      "kits":get_kits(),
    })

def choix_kit(request):
    return render(request,"analyse/marquers.html")

def analyse_resultat(request):
    N=request.session.get("N")
    H=request.session.get("H")
    
    print(f"N: {N}\nH:{H}")
    try : 
        Echantillon.set_seuil_hauteur(H)
        Echantillon.set_seuil_nbre_marqueurs(N)
        print("Attribution des taux réussi")

        Echantillon.analyse_marqueur()
        print("Fonction analyse_données réussi")
    
    except Exception as e:
        print(f"ERREUR : Chargement des données impossible \n{e}")
    
    return render(request,"analyse/resultat_analyse.html")

