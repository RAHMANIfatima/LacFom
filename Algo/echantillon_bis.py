from mere import Mere
from foetus import Foetus
from pere import Pere
from temoin import Temoin
import json


class Sample:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data or {}
    
    @classmethod
    def load_json(self, filename):
    """Charge un fichier JSON et retourne son contenu."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erreur de chargement du fichier {filename}: {e}")
        raise  # Relance l'exception après l'avoir loggée


class Concordance:
    #contantes qui servent juste à représenter les valeurs oui ou non
    OUI = "OUI"
    NON = "NON"

class ADNAnalyzer:
    def __init__(self, foetus, mere, pere=None, seuil_hauteur=0.8):
         """
        Constructeur de la classe ADNAnalyzer.

        Parameters:
            foetus : Objet représentant les informations du fœtus.
            mere : Objet représentant les informations de la mère.
            pere : Objet représentant les informations du père (optionnel).
            seuil_hauteur : Seuil de hauteur de pic pour l'analyse (par défaut 0.8).
        """
        self.foetus = foetus
        self.mere = mere
        self.pere = pere
        self.seuil_hauteur = seuil_hauteur
        self.concordance_mere_foet = None
        self.concordance_pere_foet = None

        # chargement des fichiers json : kit.json et tpos.json directement
        self.kit_data = self.load_json('kit.json')
        self.tpos_data = self.load_json('tpos.json')
    
    def load_json(self, filename):
         """
        Charge un fichier JSON et retourne son contenu sous forme de dictionnaire.

        Parameters:
            filename : Nom du fichier JSON à charger.
        
        Returns:
            dict : Contenu du fichier JSON sous forme de dictionnaire ou un dictionnaire vide en cas d'erreur.
        """
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Erreur de chargement du fichier {filename}: {e}")
            return {}

    def common_element(self, list1, list2):
         """
        Vérifie s'il y a un élément commun entre deux listes.

        Parameters:
            list1 : Première liste à comparer.
            list2 : Seconde liste à comparer.
        
        Returns:
            bool : True si un élément est commun entre les deux listes, sinon False.
        """
        return bool(set(list1) & set(list2))

    def concordance_ADN(self, number_mere=1, number_pere=1):
         """
        Analyse la concordance ADN entre le fœtus, la mère et le père.

        Parameters:
            number_mere : Nombre maximal d'éléments non concordants entre la mère et le fœtus pour considérer que la concordance est OK (par défaut 1).
            number_pere : Nombre maximal d'éléments non concordants entre le père et le fœtus pour considérer que la concordance est OK (par défaut 1).
        """
        concordance_mere_foet = 0 #création d'un compteur des discordances entre la mère et le fœtus
        concordance_pere_foet = 0#création d'un compteur des discordances entre le père et le fœtus

        for key in self.mere.data.keys():
            self.foetus.data[key]["concordance"] = [Concordance.OUI, Concordance.OUI]

            # on verifie la concordance entre la mère et le foetus
            if not self.common_element(self.mere.data[key].get('Allele', []), self.foetus.data[key].get('Allele', [])):
                self.foetus.data[key]["concordance"][0] = Concordance.NON
                concordance_mere_foet += 1

            # on verifie la concordance entre le père et le foetus
            if self.pere:
                try:
                    if not self.common_element(self.pere.data.get(key, {}).get('Allele', []), self.foetus.data[key].get('Allele', [])):
                        self.foetus.data[key]["concordance"][1] = Concordance.NON
                        concordance_pere_foet += 1
                except KeyError:
                    pass
        # on calcul la concordance
        # on détermine si la concordance entre la mère et le fœtus est acceptable
        # le nombre de discordances est inférieur au seuil donné ou pas
        self.concordance_mere_foet = concordance_mere_foet < number_mere
        #si le père existe --> on détermine aussi si la concordance entre le père et le fœtus est acceptable
        if self.pere:
            self.concordance_pere_foet = concordance_pere_foet < number_pere


    def analyse_marqueur(self):
        """
    Analyse les marqueurs génétiques du fœtus et évalue leur contamination
    en fonction des données de la mère, des témoins positifs (tpos) et d'un seuil de hauteur de pic.

    La méthode fait plusieurs vérifications pour déterminer si un marqueur est contaminé ou non, et
    fournit des détails supplémentaires sur chaque marqueur.
    """
            marqueurs = list(self.foetus.data)  # on créer une liste des marqueurs présents dans les données du fœtus
            if 'AMEL' in marqueurs:
                marqueurs.remove('AMEL')
    
            kit_markers = self.kit_data.get("kitPP16", [])
        # on parcourt chaque marqueur dans la liste des marqueurs du fœtus
            for marqueur in marqueurs:
                if marqueur in kit_markers: #  s'il fait partie des marqueurs du kit 
                    # s'il est aussi dans les données du tpos on récupere les valeurs associées
                    if marqueur in self.tpos_data:
                        tpos_values = self.tpos_data[marqueur]
                        # ajout des valeurs TPO au fœtus pour ce marqueur
                        self.foetus.data[marqueur]["TPO"] = tpos_values
    
                    # verifie que la mère est homozygote--> si oui : le marqueur est considéré comme non informatif
                    if len(self.mere.data[marqueur]["Allele"]) == 1:
                        self.foetus.data[marqueur]["détails"] = "Mère homozygote"
                        self.foetus.data[marqueur]["conclusion"] = "Non informatif"
                    #  pas homozygote --> donc vérification de s'il y a concordance avec les allèles du fœtus
                    elif len(set(self.foetus.data[marqueur]["Allele"]).intersection(set(self.mere.data[marqueur]["Allele"]))) == 2:
                        pic1 = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(self.mere.data[marqueur]["Allele"][0])]
                        pic2 = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(self.mere.data[marqueur]["Allele"][1])]
    
                        if abs(pic1 - pic2) > (1 - self.seuil_hauteur) * max(pic1, pic2):
                            contaminant = min(pic1, pic2)
                            pic_conta = self.foetus.data[marqueur]["Allele"][self.foetus.data[marqueur]["Hauteur"].index(contaminant)]
                            ECHO = False
    
                            for pic_foetus in self.foetus.data[marqueur]["Allele"]:
                                if round(abs(pic_foetus - pic_conta), 2) == 1.0:
                                    ECHO = True
                                    self.foetus.data[marqueur]["conclusion"] = "Non informatif"
                                    self.foetus.data[marqueur]["détails"] = "Echo"
                                    break
    
                        # si pas d'écho trouvé --> calcule du pourcentage de contamination et marquer le marqueur comme contaminé
                            if not ECHO:
                                pourcentage = (contaminant / (contaminant + pic_conta)) * 100
                                self.foetus.data[marqueur]["conclusion"] = "Contaminé"
                                self.foetus.data[marqueur]["détails"] = round(pourcentage, 2)
                        else:
                        #  pics ne sont pas suffisamment différents --> marqueur  considéré comme non contaminé
                            self.foetus.data[marqueur]["conclusion"] = "Non contaminé"
                            self.foetus.data[marqueur]["détails"] = ""
    

class Echantillon:
    def __init__(self, date, mere, foetus, tpos, tneg, pere=None, seuil_nbre_marqueurs=2, seuil_hauteur=1/3):
        self.date = date
        self.mere = Mere(*mere)
        self.foetus = Foetus(*foetus)
        self.tpos = Temoin(*tpos)
        self.tneg = Temoin(*tneg)
        self.pere = Pere(*pere) if pere else None
        self.seuil_nbre_marqueurs = seuil_nbre_marqueurs
        self.seuil_hauteur = seuil_hauteur
        self.analyzer = ADNAnalyzer(self.foetus, self.mere, self.pere, seuil_hauteur)
   
    
    
    def get_resultats(self):
        """
        Dictionnary  of all results
        """
        marqueurs = list(self.foetus.data)
        marqueurs.remove("AMEL")
        if self.concordance_mere_foet:
            if self.pere:
                if self.concordance_pere_foet:
                    resultat = {"Marqueur": marqueurs,
                                "Conclusion": [self.foetus.data[marqueur]["conclusion"] for marqueur in marqueurs],
                                "Détails M/F": [self.foetus.data[marqueur]["détails"] for marqueur in marqueurs]}
                else:
                    resultat = {"Marqueur": marqueurs,
                                "Conclusion": [self.foetus.data[marqueur]["conclusion"] for marqueur in marqueurs],
                                "Détails M/F": [self.foetus.data[marqueur]["détails"] for marqueur in marqueurs],
                                "Concordance Pere/Foetus": [self.foetus.data[marqueur]["concordance"][1] for marqueur in marqueurs], "Détails P/F": self.get_notconcordant(1)}
            else:
                resultat = {"Marqueur": marqueurs,
                            "Conclusion": [self.foetus.data[marqueur]["conclusion"] for marqueur in marqueurs],
                            "Détails M/F": [self.foetus.data[marqueur]["détails"] for marqueur in marqueurs]}
        else:
            if self.pere:
                if self.concordance_pere_foet:
                    resultat = {"Marqueur": marqueurs, "Concordance Mere/Foetus": [self.foetus.data[marqueur]["concordance"][0] for marqueur in marqueurs], "Détails M/F": self.get_notconcordant(0)}
                else:
                    resultat = {"Marqueur": marqueurs, "Concordance Mere/Foetus": [self.foetus.data[marqueur]["concordance"][0] for marqueur in marqueurs], "Détails M/F": self.get_notconcordant(0), "Concordance Pere/Foetus": [self.foetus.data[marqueur]["concordance"][1] for marqueur in marqueurs], "Détails P/F": self.get_notconcordant(1)}
            else:
                resultat = {"Marqueur": marqueurs, "Concordance Mere/Foetus": [self.foetus.data[marqueur]["concordance"][0] for marqueur in marqueurs], "Détails M/F": self.get_notconcordant(0)}
        return resultat
