# -*- coding: utf-8 -*-

import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from time import strftime
import re
from .echantillon import *
#from individus import *
#from mere import *
#from foetus import *
#from pere import *


heure = datetime.now()
heure_vrai = heure.strftime("%d-%m-%Y_%Hh_%Mm")
logging.basicConfig(filename='log_' + heure_vrai + '.txt', filemode='w', format='%(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def lecture_fichier(path_data_frame):
    data = []
    logger.info("Ouverture du fichier")

    try:
        #file_ = open(path_data_frame, "r")
        #for line in file_.readlines():
        #    print(line, line.split('\t'), len(line.split('\t')))
        #file_.close()
        donnees = pd.read_csv(path_data_frame, sep='\t', header=0, keep_default_na=False)
        # cast Allele and Height data as float
        #tmp = donnees.columns.tolist()[6:] #TODO: optimiser car nom Allele et Height
        #donnees = donnees.astype(dict(zip(tmp, [float]*len(tmp))))
    except Exception as e:
        logger.error("Ouverture impossible", exc_info=True)
        # 1: ouverture impossible
        return "ouverture impossible"

    logger.info("Chargement des données")
    # Check the presence of TPOS and TNEG
    if donnees[donnees["Sample Name"].str.contains(r'T.*POS|T\+|[Tt]?emoin[ ]?\+|[Tt]?emoin[ ]?[POS|positif]', regex=True) == True].shape[0] == 0:
        logger.error("Temoin positif absent", exc_info=True)
        # 2: T POS absent
        return "T POS absent"
    elif donnees[donnees["Sample Name"].str.contains(r'T.*NEG|T\-|[Tt]?emoin[ ]?\-|[Tt]?emoin[ ]?[NEG|negatif]|BLANC|BLC|Blanc', regex=True) == True].shape[0] == 0:
        logger.error("Temoin negatif absent", exc_info=True)
        # 3: T NEG absent
        return "T NEG absent"
    # Check the presence of the father
    elif donnees.shape[0]%5 == 0 or donnees.shape[0]%4 == 0:
        logger.error("Presence ou Absence des données du pere", exc_info=True)
        #iterateur = donnees["Sample Name"].nunique()
    else:
        # 4: Nombre de lignes incorrect
        logger.error("Nombre de lignes incompatible", exc_info=True)
        return "Nombre de lignes incorrect"

    # Normalisation TPOS and TNEG name
    donnees.loc[donnees["Sample Name"].str.contains(r'T.*POS|T\+|[Tt]?emoin[ ]?\+|[Tt]?emoin[ ]?[POS|positif]', regex=True) == True, "Sample Name"] = "TPOS"
    donnees.loc[donnees["Sample Name"].str.contains(r'T.*NEG|T\-|[Tt]?emoin[ ]?\-|[Tt]?emoin[ ]?[NEG|negatif]|BLANC|BLC|Blanc', regex=True)== True, "Sample Name"] = "TNEG"

    # Get sample names to associate
    allsamples = pd.unique(donnees["Sample Name"]).tolist()
    allsamples.remove("TPOS")
    allsamples.remove("TNEG")

    return [allsamples, donnees]

def computedata(samples, donnees):
    """
    samples: dictionnary of samples names with their type (mother, foetus, father)
    donnees: dataframe of data with TPOS and TNEG names normalized
    return the object echantillon with the composition of the analysis
    """
    # Get data
    try:
        date_echantillon = re.search("(\d{4}-\d{2}-\d{2})", donnees["Sample File"].values[0]).group()
    except:
        date_echantillon = str(heure.year)+"-"+str(heure.month)+"-"+str(heure.day)

    data = []

    for value in [samples["mother"], samples["foetus"], "TPOS", "TNEG"]:
        data.append([value, {}])
        for index, row in donnees[donnees["Sample Name"] == value].iterrows():
            data[-1][1][row["Marker"]] = {}
            data[-1][1][row["Marker"]]["Allele"] = getdata(row, "Allele")
            data[-1][1][row["Marker"]]["Hauteur"] = getdata(row, "Height")
            if len(data[-1][1][row["Marker"]]["Allele"]) != len(data[-1][1][row["Marker"]]["Hauteur"]):
                # Le marqueur "dans le log" n'a pas le meme nombre d'alleles que de hauteurs
                logger.info(donnees["Marker"][ligne + i])
                return "Le marqueur n'a pas le meme nombre d'alleles que de hauteurs"
    
    if "father" in samples:
        data.append([samples["father"], {}])
        for index, row in donnees[donnees["Sample Name"] == samples["father"]].iterrows():
            data[-1][1][row["Marker"]] = {}
            data[-1][1][row["Marker"]]["Allele"] = getdata(row, "Allele")
            data[-1][1][row["Marker"]]["Hauteur"] = getdata(row, "Height")
            if len(data[-1][1][row["Marker"]]["Allele"]) != len(data[-1][1][row["Marker"]]["Hauteur"]):
                # Le marqueur "dans le log" n'a pas le meme nombre d'alleles que de hauteurs
                logger.info(donnees["Marker"][ligne + i])
                return "Le marqueur n'a pas le meme nombre d'alleles que de hauteurs"

    echantillon = Echantillon(date_echantillon, *data) #date, mere, foetus, tpos, tneg, pere = None, seuil_nbre_marqueurs=2, seuil_hauteur=1 / 3
    logger.info("Chargement des données réussi")    
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
