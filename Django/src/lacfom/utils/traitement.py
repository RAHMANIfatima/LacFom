# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from time import strftime
import re
import logging
from Algo.echantillon import *

heure = datetime.now()
heure_vrai = heure.strftime("%d-%m-%Y_%Hh_%Mm")
logging.basicConfig(filename='log_' + heure_vrai + '.txt', filemode='w', format='%(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def lecture_fichier(path_data_frame):
    """
    Adaptation de la fonction lecture_fichier(path_data_frame) du fichier traitement.py pour l'application Django

    Retourne une liste [allsamples,data]
    """
    data = []
    allsamples = []

    try:
        with open(path_data_frame, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return "ouverture impossible"

    if not lines:
        return "fichier vide"

    header = lines[0].strip().split('\t')
    if "Sample Name" not in header:
        return "colonne 'Sample Name' absente"


    for line in lines[1:]:
        cols = line.strip().split('\t')
        if len(cols) < len(header):
            cols+=[""]*(len(header)-len(cols))

        elif len(cols) > len(header):
            continue
        data.append(dict(zip(header, cols)))
    print("Lignes valides chargées :", len(data))

    if not data:
        return "aucune donnée valide"

    # sample_names = [row["Sample Name"] for row in data]

    #Check la présence de TPOS et NPOS
    # À ENLEVER AVEC LE FICHIER DE CONFIGURATION 
    # has_tpos = any("pos" in name.lower() for name in sample_names)
    # if not has_tpos:
    #     return "T POS absent"

    # has_tneg = any("neg" in name.lower() or "blanc" in name.lower() for name in sample_names)
    # if not has_tneg:
    #     return "T NEG absent"

    for row in data:
        name = row["Sample Name"].lower().strip()
        if "pos" in name:
            row["Sample Name"] = "TPOS"
        elif "neg" in name or "blanc" in name:
            row["Sample Name"] = "TNEG"

    allsamples = list(set(
        row["Sample Name"] for row in data if row["Sample Name"] not in ["TPOS", "TNEG"]
    ))

    # Check la présence de père
    if len(data) % 5 != 0 and len(data) % 4 != 0:
        return "Nombre de lignes incorrect"

    return [allsamples, data]



def computedata(samples, donnees):
    """
    samples: dictionnary of samples names with their type (mother, foetus, father)
    donnees: list dictionnary of data [{Sample files1,Sample Name1, Marker, Allele,Height},{Sample files2,Sample Name2, Marker, Allele,Height}]
    return the object echantillon with the composition of the analysis
    """
    # Get data
    try:
        date_str = donnees[0]["Sample File"]
        print(donnees[0]["Sample File"])
        match = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
        if match:
            date_echantillon = match.group()
            print("match")
        else:
            raise ValueError
    except:
        now = datetime.now()
        date_echantillon = f"{now.year}-{now.month:02}-{now.day:02}"

    data = []
    print("Début computedata")
    # print(f"Samples : {samples}\nDonnees : {donnees}\n")

    for value in [samples["mother"], samples["foetus"], "TPOS", "TNEG"]:
        data.append([value, {}])
        lignes = [row for row in donnees if row["Sample Name"] == value]

        for row in lignes:
            marker = row["Marker"]
            data[-1][1][marker] = {}
            data[-1][1][marker]["Allele"] = getdata(row, "Allele")
            data[-1][1][marker]["Hauteur"] = getdata(row, "Height")
            if len(data[-1][1][marker]["Allele"]) != len(data[-1][1][marker]["Hauteur"]):
                print(f"Incohérence dans {marker} pour {value}")
                return "Le marqueur n'a pas le même nombre d'allèles que de hauteurs"

    
    print("début if father")
    if "father" in samples:
        data.append([samples["father"], {}])
        lignes = [row for row in donnees if row["Sample Name"] == samples["father"]]

        for row in lignes:
            marker = row["Marker"]
            data[-1][1][marker] = {}
            data[-1][1][marker]["Allele"] = getdata(row, "Allele")
            data[-1][1][marker]["Hauteur"] = getdata(row, "Height")
            if len(data[-1][1][marker]["Allele"]) != len(data[-1][1][marker]["Hauteur"]):
                print(f"Incohérence dans {marker} pour père")
                return "Le marqueur n'a pas le même nombre d'allèles que de hauteurs"

    print("Attribution class Echantillon")
    print("Attribution class Echantillon")
    echantillon = Echantillon(date_echantillon, *data) #date, mere, foetus, tpos, tneg, pere = None, seuil_nbre_marqueurs=2, seuil_hauteur=1 / 3
    logger.info("Chargement des données réussi")
    print("Computedata fini")    
    return echantillon

def getdata(line, name):
    data = []
    for key in line.keys():
        if name in key and line[key] in ['X', 'Y', '?']:
            data.append(line[key])
        elif name in key and line[key] != "":
            data.append(float(line[key]))
    return data

def concordance_ADN(echantillon):
    logger.info("Check mother sex")
    if not echantillon.mere.check_sex():
        # La mere est de sexe masculin
        return "La mere est de sexe masculin"
    logger.info("Check father sex")
    if echantillon.pere and not echantillon.pere.check_sex():
        # Le pere est de sexe feminin
        return "Le pere est de sexe feminin"
    logger.info("Vérification de la concordance des ADNs")
    try:
        echantillon.concordance_ADN()
    except AttributeError:
        logger.info("Concordance ADN failled")

if __name__ == "__main__":
    file_path = sys.argv[1]
    print(file_path)
    samples, donnees = lecture_fichier(file_path)
    print(samples)
    samples = {"mother":'1-192107', "foetus":'2-200544', "father":'3-192106'}
    echantillon = computedata(samples, donnees)
    # Check temoins
    checktpos = echantillon.tpos.check()
    checktneg = echantillon.tneg.check()
    if checktpos == []:
        print("Temoin positif : validé")
    else:
        print("Témoin positif : NON VALIDE", checktpos)
    if checktneg == []:
        print("Temoin négatif : validé")
    else:
        print("Témoin négatif : NON VALIDE", checktneg)
    # Check concordance
    val = concordance_ADN(echantillon)
    print(echantillon.concordance_pere_foet)
    print(echantillon.concordance_mere_foet)
    # Do analyse
    echantillon.analyse_marqueur()
    for indice in range (len(echantillon.get_resultats()['Marqueur'])):
        print(echantillon.get_resultats()['Marqueur'][indice], ": ", echantillon.get_resultats()['Détails M/F'][indice])
    print(echantillon.get_contamine())
    print(echantillon.get_conclusion())
