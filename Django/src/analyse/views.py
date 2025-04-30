from django.shortcuts import render,redirect
from .marqueurs.marquers import get_kits, load_kits, save_kits

from Algo.echantillon import Echantillon
from Algo.individus import Individus
from Algo.foetus import Foetus
from Algo.mere import Mere
from Algo.pere import Pere
from Algo.temoin import Temoin
from lacfom.utils import traitement


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

def attribution_origine(request):
    samples=request.session.get("samples") 

    dictsamples={}

    for nom in samples:
        valeur=request.POST.get(nom)
        if valeur:
            dictsamples[valeur]=nom
    
    # if "foetus" not in dictsamples or "mother" not in dictsamples:
    #     message.error(request,"Veuillez sélectionner un foetus et un mère.")
    #     return redirect("Traiter choix")
    
    print("Attribution origine")
    
    for origine,sample in dictsamples.items():
        print(f"{origine} --> {sample}")

    request.session["dictsamples"]=dictsamples
    return redirect("analyse_resultat")

def analyse_resultat(request):
    N=request.session.get("N")
    H=request.session.get("H")
    dictsamples=request.session.get("dictsamples") 
    data=request.session.get("data")

    try : 
        echantillon = traitement.computedata(dictsamples, data)
        echantillon.InfoParametre["Echantillon"]=echantillon
        
        if N and H is not None:
            echantillon.set_seuil_hauteur(H)
            echantillon.set_seuil_nbre_marqueurs(N)
            print("Attribution des taux réussi")

        print(f"N: {echantillon.seuil_nbre_marqueurs}\nH:{echantillon.seuil_hauteur}")
        # echantillon.analyse_marqueur()
        # print("Fonction analyse_données réussi")
    
    except Exception as e:
        print(f"ERREUR : Chargement des données impossible \n{e}")
    
    return render(request,"analyse/resultat_analyse.html")