from django.shortcuts import render,redirect
from .marqueurs.marquers import get_kits, load_kits, save_kits

import pandas as pd

from Algo.echantillon import Echantillon
from Algo.individus import Individus
from Algo.foetus import Foetus
from Algo.mere import Mere
from Algo.pere import Pere
from Algo.temoin import Temoin
from Algo import traitement


def afficher_importation(request):
    """
    Permet de visuliser le contenue du fichier.
    """
    contenu = request.session.pop("contenu_fichier", None)  # Récupère le contenu et le supprime après affichage
    return render(request, "analyse/visualisation.html", {"contenu": contenu})

def traiter_choix(request):
    """
    Affiche la page d'identifaction des échantillons.
    Prends en comptes le nombre d'élements dans la variable sample et rediriges vers la page appropriée.
    """
    samples=request.session.get("samples") 
    donnees=request.session.get("donnees")
    kits=request.session.get("kits")
    # print(f"Longueur de samples2 : {len(samples)}")
    # print(f"Longueur de data2 : {len(donnees)}")
    
    if len(samples)==3:
        print("Présence d'un père")
        return render(request,"analyse/identification_avec_pere.html",{
                      "samples":samples,
                      "donnees":donnees,
                      "kits":get_kits(),
        })
    
    print("Absence de père")
    return render(request, "analyse/identification.html", {
                      "samples":samples,
                      "donnees":donnees,
                      "kits":get_kits(),
    })

def choix_kit(request):
    return render(request,"analyse/marquers.html")

def attribution_origine(request):
    """
    Attribue les échantillons à leur origine choisies dans la page d'identification
    Enregistre les origines dans un dictionnaire sous la forme {'mere':'sample1','foetus':'sample2'}
    """
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
    """
    Fonction qui crée l'instance de l'échantillon et lui attribue les paramètres et les résultats de l'analyse.
    """
    N=request.session.get("N")
    H=request.session.get("H")
    dictsamples=request.session.get("dictsamples") 
    donnees=request.session.get("donnees")

    try : 
        echantillon = traitement.computedata(dictsamples, donnees)
        # echantillon.InfoParametre["Echantillon"]=echantillon
        code=traitement.concordance_ADN(echantillon)
        if code:
            print(code)
            return redirect("traiter_choix")


        if N and H is not None: # Met à jour les valeurs changer dans Paramètres
            echantillon.set_seuil_hauteur(eval(H))
            echantillon.set_seuil_nbre_marqueurs(float(N))
            print("Attribution des taux réussi")

        print(f"N: {echantillon.seuil_nbre_marqueurs}\nH:{echantillon.seuil_hauteur}")
        echantillon.analyse_marqueur()
        print("Fonction analyse_données réussi")
    
    except Exception as e:
        print(f"ERREUR : Chargement des données impossible - {e} -")
        return redirect("traiter_choix")
    
    request.session["echantillon"]=echantillon

    return redirect("affichage_resultat")

def affichage_resultat(request):
    """
    Page d'affichage du résulat de l'analyse de l'échantillon
    """
    echantillon=request.session.get("echantillon")
    version=request.session.get("version")
    emetteur=request.session.get("emetteur")
    entite=request.session.get("entite")
    N=echantillon.seuil_nbre_marqueurs
    H=echantillon.seuil_hauteur

    if emetteur and entite is None:
        emetteur="PBP-P2A-GEN"
        entite="PBP-PTBM"


    try:
        sexe=echantillon.foetus.get_sexe()
        df_conclusion=pd.DataFrame.from_dict(echantillon.get_resultats())
        df_detail=echantillon.get_conclusion()
        code_conclu = echantillon.get_contamine()
        nom_projet = echantillon.get_id()
        nom_mere= echantillon.mere.ID
        Emetteur= emetteur
        Entite_appli = entite
        # nom_pdf=str(echantillon.get_id()) + "_" + str(self.onglets[echantillon.get_id()]) + "_" + nom_utilisateur"]
        Version= str(version)
        print("Récupération des données réussi")

        if echantillon.concordance_pere_foet == None:
            num_pere = "ABS"
            pres_pere = "ABS"
        else:
            num_pere = echantillon.pere.ID
            pres_pere = "OUI"
        num_foetus = echantillon.foetus.ID
        # filename = filename
        # path = instance_path
    except Exception as e:
        print(f"Erreur : {e}")
        return redirect("traiter_choix")

    return render(request,"analyse/resultat_analyse.html")