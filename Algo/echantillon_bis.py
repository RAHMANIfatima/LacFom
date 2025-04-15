import json

class Echantillon:

    """ Parameters used to analyze one fetal sample

    Attributes:
        date : date sample
        concordance (str) : DNAs match between mother and fetus
        seuil_nbre_marqueurs (int) : marker number which have to be contaminated to declare sample as contaminated
        seuil_hauteur (int) : spike height to check
        mere (object) : information about mother
        foetus (object) : information about fetus
        pere (object) : information about father
        tpos (object) : informations about tpos
        tneg (object) : informations about tneg
        ?? conclusion (int) : contaminated sample (1) or not (0)
    """

    def __init__(self, date, mere, foetus, tpos, tneg, pere=None, seuil_nbre_marqueurs=2, seuil_hauteur=1 / 3):
        """ The constructor for Echantillon class
        
        Parameters:
            date : date sample
            concordance (str) : DNAs match between mother and fetus
            seuil_nbre_marqueurs (int) : marker number which have to be contaminated to declare sample as contaminated
            seuil_hauteur (int) : spike height to check
            conclusion (int) : contaminated sample (1) or not (0)
        """
        self.date = date
        self.mere = Mere(*mere)
        self.foetus = Foetus(*foetus)
        self.tpos = Temoin(*tpos)
        self.tneg = Temoin(*tneg)
        if pere:
            self.pere = Pere(*pere)
        else:
            self.pere = pere
        self.seuil_nbre_marqueurs = seuil_nbre_marqueurs
        self.seuil_hauteur = seuil_hauteur
        self.concordance_mere_foet = None
        self.concordance_pere_foet = None

        # Charger les fichiers JSON
        self.kit_data = self.load_json('kit.json')
        self.tpos_data = self.load_json('tpos.json')

    def load_json(self, filename):
        """Charge un fichier JSON et le retourne sous forme de dictionnaire."""
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(f"Erreur de chargement du fichier {filename}: {e}")
            return {}

    def concordance_ADN(self, number_mere=1, number_pere=1):
        concordance_mere_foet = 0
        concordance_pere_foet = 0
        for key in self.mere.data.keys():
            self.foetus.data[key]["concordance"] = ["OUI", "OUI"]
            if not common_element(self.mere.data[key]['Allele'], self.foetus.data[key]['Allele']):
                self.foetus.data[key]["concordance"][0] = "NON"
                concordance_mere_foet += 1
            try:
                if not common_element(self.pere.data[key]['Allele'], self.foetus.data[key]['Allele']):
                    self.foetus.data[key]["concordance"][1] = "NON"
                    concordance_pere_foet += 1
            except Exception as e:
                pass
        
        # Vérifier la concordance
        self.concordance_mere_foet = True
        if concordance_mere_foet >= number_mere:
            self.concordance_mere_foet = False
        if self.pere and concordance_pere_foet >= number_pere:
            self.concordance_pere_foet = False
        elif self.pere:
            self.concordance_pere_foet = True

    def analyse_marqueur(self):
        """
        Analyser les marqueurs en utilisant les données du fichier JSON
        """
        marqueurs = list(self.foetus.data)
        marqueurs.remove('AMEL')

        # Utilisation de kit.json
        kit_markers = self.kit_data.get("kitPP16", [])

        for marqueur in marqueurs:
            if marqueur in kit_markers:
                # Logic for analysis based on marker presence in the kit
                if marqueur in self.tpos_data:
                    tpos_values = self.tpos_data[marqueur]
                    # Update foetus data based on tpos values
                    self.foetus.data[marqueur]["TPO"] = tpos_values

                # Logique d'analyse spécifique pour les autres marqueurs
                if len(self.mere.data[marqueur]["Allele"]) == 1:
                    self.foetus.data[marqueur]["détails"] = "Mère homozygote"
                    self.foetus.data[marqueur]["conclusion"] = "Non informatif"
                # Alleles mere inclus dans alleles foetus:
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
                        if not ECHO:
                            self.foetus.data[marqueur]["conclusion"] = "Contaminé"
                            self.foetus.data[marqueur]["détails"] = round((contaminant / (contaminant + pic_conta)) * 100, 2)
                    else:
                        self.foetus.data[marqueur]["conclusion"] = "Non contaminé"
                        self.foetus.data[marqueur]["détails"] = ""

    # Ajoutez d'autres méthodes nécessaires pour le traitement avec les fichiers JSON ici.

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
