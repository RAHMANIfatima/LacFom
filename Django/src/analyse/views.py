import ast
from django.shortcuts import render,redirect
from .marqueurs.marquers import get_kits, load_kits, save_kits

import pandas as pd
import json

from Algo.echantillon import Echantillon
from Algo.individus import Individus
from Algo.foetus import Foetus
from Algo.mere import Mere
from Algo.pere import Pere
from Algo.temoin import Temoin
from Algo import traitement
from django.core.files.storage import FileSystemStorage


def afficher_importation(request):
    """
    Permet de visuliser le contenue du fichier.
    """
    contenu = request.session.pop("contenu_fichier", None)  # Récupère le contenu et le supprime après affichage
    return render(request, "analyse/visualisation.html", {"contenu": contenu})

def traiter_choix(request):
    """
    Affiche la page d'identification des échantillons.
    Prend en compte le nombre d'éléments dans la variable sample et redirige vers la page appropriée.
    """
    samples = request.session.get("samples")
    donnees = request.session.get("donnees")

    if samples and len(samples) == 3:
        print("Présence d'un père")
        return render(request, "analyse/identification_avec_pere.html", {
            "samples": samples,
            "donnees": donnees,
        })

    print("Absence de père")
    return render(request, "analyse/identification.html", {
        "samples": samples,
        "donnees": donnees,
    })

def choix_kit(request):
    return render(request,"analyse/marquers.html")

def attribution_origine(request):
    """
    Attribue les échantillons à leur origine choisies dans la page d'identification.
    Enregistre les origines dans un dictionnaire sous la forme {'mere':'sample1','foetus':'sample2'}.
    Gère également les données du kit si elles sont présentes.
    """
    samples = request.session.get("samples")
    kit_data = request.POST.get("kit_data")  # Récupérer les données du kit depuis le formulaire

    # Si kit_data est présent dans le formulaire, le stocker dans la session
    if kit_data:
        try:
            kit_data = json.loads(kit_data)  # Convertir en dictionnaire
            request.session["kit_data"] = kit_data
        except json.JSONDecodeError:
            print("Erreur : données du kit invalides.")
            kit_data = None

    dictsamples = {}

    # Récupérer les choix des utilisateurs pour chaque échantillon
    for nom in samples:
        valeur = request.POST.get(nom)
        if valeur:
            dictsamples[valeur] = nom

    print("Attribution origine")
    for origine, sample in dictsamples.items():
        print(f"{origine} --> {sample}")

    # Stocker les données dans la session
    request.session["dictsamples"] = dictsamples

    return redirect("analyse_resultat")

def analyse_resultat(request):
    """
    Fonction qui crée l'instance de l'échantillon et lui attribue les paramètres et les résultats de l'analyse.
    """
    N=request.session.get("N")
    H=request.session.get("H")
    dictsamples=request.session.get("dictsamples") 
    donnees=request.session.get("donnees")
    selected_kit = request.session.get("kit_data")  # Récupérer le kit sélectionné
    try:
        if selected_kit and isinstance(selected_kit, str):
            selected_kit = ast.literal_eval(selected_kit)
    except:
        print("une erreur est survenue lors de la conversion du kit")
        selected_kit = None

    try : 
        echantillon = traitement.computedata(dictsamples, donnees,selected_kit)
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
    Page d'affichage du résulat de l'analyse de l'échantillon.
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
        df_conclusion=pd.DataFrame.from_dict(echantillon.get_resultats()) #DF avec Marqueur | Conclusion | Détail M/F
        df_detail=echantillon.get_conclusion()
        code_conclu = echantillon.get_contamine()
        nom_projet = echantillon.get_id()
        num_mere= echantillon.mere.ID
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

    tableau_resultat=df_conclusion.to_html(classes="table table-bordered w-100", index=False)
    
    print(df_detail)

    return render (request,"analyse/resultat_analyse.html",{
        "resultat":tableau_resultat,
        "nom_projet":nom_projet,
        "num_mere":num_mere,
        "num_pere":num_pere,
        "pres_pere":pres_pere,
        "num_foetus":num_foetus,
        "sexe":sexe,
        "N":N,
        "H":H,
        })