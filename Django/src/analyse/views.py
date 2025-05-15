import ast
from django.shortcuts import render,redirect
from .marqueurs.marquers import get_kits, load_kits, save_kits
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse,JsonResponse
from django.conf import settings

import pandas as pd
import json
import os
import json

from Algo.echantillon import Echantillon
from Algo.individus import Individus
from Algo.foetus import Foetus
from Algo.mere import Mere
from Algo.pere import Pere
from Algo.temoin import Temoin
from Algo import traitement
from Algo import pdf_feuille_resultat
from Algo.kit import Kit



def afficher_importation(request):
    """
    Permet de visuliser le contenue du fichier.
    """
    contenu = request.session.get("chemin_fichier", None)
    try:
        df = pd.read_csv(contenu, sep="\t", dtype=str)
        df = df.fillna("")  # Remplir les valeurs vides pour éviter les NaN
        table_html = df.to_html(classes="table table-bordered table-striped", index=False, border=0)
    except Exception as e:
        table_html = f"<p>Erreur lors de la lecture du fichier : {e}</p>"

    return render(request, "analyse/visualisation.html", {"table_html": table_html})

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
    """
    samples = request.session.get("samples")
    kit_data = get_kit_from_request_or_default(request)

    dictsamples = {}
    for nom in samples:
        valeur = request.POST.get(nom)
        if valeur:
            dictsamples[valeur] = nom
    
    if "foetus" not in dictsamples or "mother" not in dictsamples:
        messages.error(request, "Veuillez sélectionner un foetus et une mère.")
        return redirect("Traiter_choix")
    
    print("Attribution origine")
    for origine, sample in dictsamples.items():
        print(f"{origine} --> {sample}")

    # Stocker les données dans la session
    request.session["dictsamples"] = dictsamples
    request.session["kit_data"] = kit_data  # Mettre à jour le kit utilisé dans la session

    return redirect("analyse_resultat")

def analyse_resultat(request):
    """
    Fonction qui crée l'instance de l'échantillon et lui attribue les paramètres et les résultats de l'analyse.
    """
    N = request.session.get("N")
    H = request.session.get("H")
    dictsamples = request.session.get("dictsamples") 
    donnees = request.session.get("donnees")
    samples = request.session.get("samples")
    selected_kit = get_kit_from_request_or_default(request)

    try:
        echantillon = traitement.computedata(dictsamples, donnees, selected_kit)
        code = traitement.concordance_ADN(echantillon)
        if code:
            messages.error(request, code)
            return redirect("traiter_choix")

        if N and H is not None:  # Met à jour les valeurs changées dans Paramètres
            echantillon.set_seuil_hauteur(eval(H))
            echantillon.set_seuil_nbre_marqueurs(float(N))
            print("Attribution des taux réussi")

        echantillon.analyse_marqueur()
        print("Fonction analyse_données réussi")
    
    except Exception as e:
        print(f"ERREUR : Chargement des données impossible - {e} -")
        messages.error(request, "Chargement des données impossible")
        return redirect("traiter_choix")
    
    request.session["echantillon"] = echantillon

    return redirect("affichage_resultat")

def affichage_resultat(request):
    """
    Page d'affichage du résulat de l'analyse de l'échantillon.
    """
    echantillon=request.session.get("echantillon")
    N=echantillon.seuil_nbre_marqueurs
    H=echantillon.seuil_hauteur

    try:
        sexe=echantillon.foetus.get_sexe()
        dict_resultat=echantillon.get_resultats() #DF avec Marqueur | Conclusion | Détails
        df_detail=echantillon.get_conclusion()
        code_conclu = echantillon.get_contamine()
        nom_projet = echantillon.get_id()
        num_mere= echantillon.mere.ID
        # nom_pdf=str(echantillon.get_id()) + "_" + str(self.onglets[echantillon.get_id()]) + "_" + nom_utilisateur"]
        is_tpos=len(echantillon.tpos.check())==0
        is_tneg=len(echantillon.tneg.check())>0
        
        if len(echantillon.tpos.check()) > 0:
            is_tpos = False
            code_tpos=0
        else:
            is_tpos = True
            code_tpos=1
        if len(echantillon.tneg.check()) > 0:
            is_tneg = False
            code_tneg=0
        else:
            is_tneg = True
            code_tneg=1
            

        # print(f"Tpos : {echantillon.tpos.check()}\nTneg :{echantillon.tneg.check()}")

        if echantillon.concordance_mere_foet is True:
            concordance_mere_foet="OUI"
        else :
            concordance_mere_foet="NON"
        if echantillon.concordance_pere_foet is None:
            concordance_pere_foet="ABS"
        elif echantillon.concordance_pere_foet is True :
            concordance_pere_foet="OUI"
        else:
            concordance_pere_foet="NON"

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

        nb_marqueurs_informatifs_non_contaminés=df_detail[0]
        nb_marqueurs_informatifs_contaminés=df_detail[1]
        moyenne_conta=df_detail[2]

        is_conta=code_conclu >1 # Si l'échantillon est non-significativement contaminé, il sera marqué comme contaminé

        print(f"Temoin : {echantillon.tpos.kit.get_tpos_data()}")

    except Exception as e:
        print(f"Erreur : {e}")
        messages.error(request,"Chargement des données impossible")
        return redirect("traiter_choix")

    # tableau_resultat=df_conclusion.to_html(classes="table table-bordered w-100", index=False) #TODO Faire en sorte que quand la conclusion est "non contaminé" la ligne soit verte et si la conclusion est "contaminé" la ligne est rouge
    #Besoin importer Jinja2 ?

    request.session["code_tpos"]=code_tpos
    request.session["code_tneg"]=code_tneg

    # print(df_detail)
    # print(f"code_conclu: {code_conclu}")
    print(f"dict_resultat : {dict_resultat}")
    
    ########################## PREPARATION DU TABLEAU ##########################
    ndict_resultat=[
        {'Marqueur': m, 'Conclusion': c, 'Détails_M_F': d}
        for m, c, d in zip(dict_resultat['Marqueur'], dict_resultat['Conclusion'], dict_resultat['Détails_M_F'])
    ]


    return render (request,"analyse/resultat_analyse.html",{
        "dict_resultat":ndict_resultat,
        "nom_projet":nom_projet,
        "num_mere":num_mere,
        "num_pere":num_pere,
        "pres_pere":pres_pere,
        "num_foetus":num_foetus,
        "sexe":sexe,
        "is_tpos":is_tpos,
        "is_tneg":is_tneg,
        "concordance_mere_foet":concordance_mere_foet,
        "concordance_pere_foet":concordance_pere_foet,
        "nb_marqueurs_informatifs_non_contaminés":nb_marqueurs_informatifs_non_contaminés,
        "nb_marqueurs_informatifs_contaminés":nb_marqueurs_informatifs_contaminés,
        "moyenne_conta":moyenne_conta,
        "N":N,
        "H":round(H,2),
        "is_conta":is_conta,
        })



def change_radio_selection(request):
    if request.method == "POST":
        data = json.loads(request.body)
        choix = data.get("contamination")
        print(f"Choix reçu côté serveur : {choix}")
        if choix == "non-contamine":
            code_choix=0
        else:
            code_choix=1
        request.session["contamination"] = code_choix
        return JsonResponse({"status": "ok", "choix": choix})
    return JsonResponse({"error": "Invalid request"}, status=400)



def exportation_pdf(request):
    """
    Exportation des résultats en pdf
    """
    echantillon=request.session.get("echantillon")
    code_tpos=request.session.get("code_tpos")
    code_tneg=request.session.get("code_tneg")
    code_conclu = echantillon.get_contamine()
    choix=request.session.get("contamination")
    nom_utilisateur="User_test"
    emetteur=request.session.get("emetteur")
    entite=request.session.get("entite")
    version=request.session.get("version")
    N=request.session.get("N")
    H=request.session.get("H")
    nom_pdf=str(echantillon.get_id()) + "_" + nom_utilisateur
    chemin_pdf=os.path.join(settings.MEDIA_ROOT, (nom_pdf + ".pdf"))

    # print(f"emetteur1 : {emetteur}\tentité : {entite}")

    if emetteur or entite is None:
        emetteur="PBP-P2A-GEN"
        entite="PBP-PTBM"
        N="2"
        H="1/3"

    print(f"choix : {choix}\tConclusion : {code_conclu}")
    if choix is None :
        choix=0
    try:
        if (choix == 0 and code_conclu == 0):
            conclu = 0
        elif (choix == 1 and code_conclu == 1):
            conclu = 1
        elif (choix == 0 and code_conclu == 1):
            conclu = 2
        elif (choix == 1 and code_conclu == 0):
            conclu = 3
        elif (choix == 0 and code_conclu == 2):
            conclu = 4
        elif (choix == 1 and code_conclu == 2):
            conclu = 5
        else:
            conclu = 6
    except Exception as e:
        messages.error("Echec attribution variable conclu")
        return

    # print(f"emetteur : {emetteur}\tentité : {entite}")
    # print(f"TPOS : {code_tpos}\t TNEG : {code_tneg} ")


    try:
        pdf_feuille_resultat.creation_PDF(settings.MEDIA_ROOT,
                                          echantillon,
                                          nom_pdf,
                                          conclu,
                                          nom_utilisateur,
                                          H,
                                          N,
                                          None,
                                          code_tpos,
                                          code_tneg,
                                          entite,
                                          emetteur,
                                          version)
        return FileResponse(open(chemin_pdf, 'rb'), content_type='application/pdf')

    except KeyError as e:
        print(f"Échec lancement création pdf : {e}")
        return redirect("affichage_resultat")
    
    
def get_kit_from_request_or_default(request):
    """
    Récupère le kit depuis la requête POST ou la session. Si aucun kit n'est trouvé, charge le kit par défaut.
    """
    kit_data = request.POST.get("kit_data")
    if kit_data:
        try:
            kit_data = json.loads(kit_data)
            print("Kit personnalisé chargé :", kit_data)
            request.session["kit_data"] = kit_data
            return kit_data
        except json.JSONDecodeError:
            print("Erreur : données du kit personnalisé invalides.")
    
    # Fallback : charger depuis la session ou par défaut
    kit_data = request.session.get("kit_data")
    if not kit_data:
        kit_object = Kit()
        kit_data = {
            "name": kit_object.name,
            "TPOS": kit_object.get_tpos_data()
        }
        print("Kit par défaut chargé :", kit_data)
        request.session["kit_data"] = kit_data
    return kit_data