from mere import *
from foetus import *
from pere import *
from temoin import *


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

    def __init__(self, date, mere, foetus, tpos, tneg, pere = None, seuil_nbre_marqueurs=2, seuil_hauteur=1 / 3):
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
        #self.echelle_allelique = self.get_echelle_allelique("echelleAlleliquePP16.txt")

    def set_seuil_nbre_marqueurs(self, nb):
        """ Set seuil_nbre_marqueurs
        """
        self.seuil_nbre_marqueurs = nb

    def set_seuil_hauteur(self, hauteur):
        """ Set seuil_hauteur
        """
        self.seuil_hauteur = hauteur

    def concordance_ADN(self, number_mere=1, number_pere=1):
        #print("-----------CONCORDANCE ADN------------")
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
        
        # Check concordance
        self.concordance_mere_foet = True
        if concordance_mere_foet >= number_mere:
            self.concordance_mere_foet = False
        if self.pere and concordance_pere_foet >= number_pere:
            self.concordance_pere_foet = False
        elif self.pere:
            self.concordance_pere_foet = True

    def analyse_marqueur(self):
        """
        """
        marqueurs = list(self.foetus.data)
        marqueurs.remove('AMEL')
        for marqueur in marqueurs:
            # check if the mother is homozygote
            if len(self.mere.data[marqueur]["Allele"]) == 1:
                self.foetus.data[marqueur]["détails"] = "Mère homozygote"
                self.foetus.data[marqueur]["conclusion"] = "Non informatif"
            # Alleles mere inclus dans alleles foetus:
            elif len(set(self.foetus.data[marqueur]["Allele"]).intersection(set(self.mere.data[marqueur]["Allele"]))) == 2:
                pic1 = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(self.mere.data[marqueur]["Allele"][0])]
                pic2 = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(self.mere.data[marqueur]["Allele"][1])]
                # diff entre les 2 pics sup a 1-seuil
                #print("pic1:",pic1,"pic2:", pic2)
                if abs(pic1 - pic2) > (1 - self.seuil_hauteur) * max(pic1,pic2) :
                    # vérification de l'echo
                    contaminant = min(pic1, pic2)
                    pic_conta = self.foetus.data[marqueur]["Allele"][self.foetus.data[marqueur]["Hauteur"].index(contaminant)]
                    # Test petit pic dans echo
                    ECHO = False
                    #print("conta",contaminant,pic_conta)
                    for pic_foetus in self.foetus.data[marqueur]["Allele"]:
                        #print("difference: ",pic_foetus, pic_conta,round(abs(pic_foetus - pic_conta),2))
                        if round(pic_foetus - pic_conta,2) == 1.0:
                            ECHO = True
                            self.foetus.data[marqueur]["conclusion"] = "Non informatif"
                            self.foetus.data[marqueur]["détails"] = "Echo"
                            break
                    if not ECHO:
                        self.foetus.data[marqueur]["conclusion"] = "Contaminé"
                        # si 3 pic conta htz sinon conta hmz
                        if len(self.foetus.data[marqueur]["Allele"]) == 3:
                            pic = list(set(self.foetus.data[marqueur]["Allele"]) - set(self.mere.data[marqueur]["Allele"]))[0]
                            pic_pere = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(pic)]
                            self.foetus.data[marqueur]["détails"] = round((contaminant / (contaminant + pic_pere)) * 100, 2)
                        else:
                            autre = max(self.foetus.data[marqueur]["Hauteur"])
                            self.foetus.data[marqueur]["détails"] = round(((2 * contaminant) / (contaminant + autre)) * 100, 2)
                else:
                    # Conta majeur
                    if len(self.foetus.data[marqueur]["Allele"]) == 3:
                        pic = list(set(self.foetus.data[marqueur]["Allele"]) - set(self.mere.data[marqueur]["Allele"]))[0]
                        pic_pere = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(pic)]
                        self.foetus.data[marqueur]["conclusion"] = "Contaminé"
                        self.foetus.data[marqueur]["détails"] = [round((pic1 / (pic1 + pic_pere)) * 100,2), round((pic2 / (pic2 + pic_pere)) * 100, 2)]
                    # Meme allele que la mere 
                    else:
                        self.foetus.data[marqueur]["conclusion"] = "Non informatif"
                        self.foetus.data[marqueur]["détails"] = "Mêmes allèles que la mère"

            # check allele foetus à n+1 de la mere ( mere dans echo a -1 de la mere [reste plus que les cas 2 alleles])
            #elif common_element([ x-1 for x in list(set(self.foetus.data[marqueur]["Allele"]).difference(set(self.mere.data[marqueur]["Allele"]))) ], list(set(self.mere.data[marqueur]["Allele"]).difference(set(self.foetus.data[marqueur]["Allele"])))):
            elif common_element([ x-1 for x in self.foetus.data[marqueur]["Allele"] ], list(set(self.mere.data[marqueur]["Allele"]).difference(set(self.foetus.data[marqueur]["Allele"])))):
                self.foetus.data[marqueur]["détails"] = "Echo"
                self.foetus.data[marqueur]["conclusion"] = "Non informatif"
            else:
                self.foetus.data[marqueur]["conclusion"] = "Non contaminé"
                self.foetus.data[marqueur]["détails"] = ""

        # Compute conclusion
        contamajeur = False
        conta = 0
        nonconta = 0
        valconta = 0
        # Nb de marqueurs informatifs non contamines
        for marqueur in marqueurs:
            if self.foetus.data[marqueur]["conclusion"] == "Non contaminé":
                nonconta += 1
            elif self.foetus.data[marqueur]["conclusion"] == "Contaminé":
                conta += 1
                if type(self.foetus.data[marqueur]["détails"]) == list:
                    contamajeur = True
                else:
                    valconta += self.foetus.data[marqueur]["détails"]
        ## Determination de la conclusion
        # Pas assez de marqueur informatifs pour conclure
        if conta+nonconta < 2:
            self.conclusion = [nonconta, conta, "-"]
            self.contamine = -1
        # nb marqueurs conta superieur au seuil
        elif conta >= self.seuil_nbre_marqueurs:
            # conta majeur
            if contamajeur:
                self.conclusion = [nonconta, conta, "MAJEURE"]
                self.contamine = 4
            # conta superieur a 5%
            elif round(valconta/conta, 2)>=5:
                self.conclusion = [nonconta, conta, round(valconta / conta, 2)]
                self.contamine = 3
            # conta inf a 5%
            else:
                self.conclusion = [nonconta, conta, str(round(valconta / conta, 2)) + " (Biologiquement non significatif)"]
                self.contamine = 2
        # aucun marqueur contamine
        elif conta == 0:
            self.conclusion = [nonconta, conta, 0]
            self.contamine = 0
        # nb de marqueurs conta inf au seuil
        else:
            self.conclusion = [nonconta, conta, round(valconta / conta, 2)]
            self.contamine = 1

        """
        if contamajeur:
            self.conclusion = [nonconta, conta, "MAJEURE"]
        elif conta == 0:
            self.conclusion = [nonconta, conta, 0]
        else:
            self.conclusion = [nonconta, conta, round(valconta/conta, 2)]

        # Det contamination 
        if conta >= self.seuil_nbre_marqueurs:
            if self.conclusion[2] == "MAJEURE":
                self.contamine = 1
            elif self.conclusion[2] >= 5:
                self.contamine = 1
            else:
                self.conclusion[2] = str(self.conclusion[2]) + " (Biologiquement non significatif)"
                self.contamine = 2
        else:
            self.contamine = 0
        """

    def compute_heterozygote_contamination(self, marqueur):
        pic = list(set(self.foetus.data[marqueur]["Allele"]) - set(self.mere.data[marqueur]["Allele"]))[0]
        pic_pere = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(pic)]

        pic1 = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(self.mere.data[marqueur]["Allele"][0])]
        pic2 = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(self.mere.data[marqueur]["Allele"][1])]


        if abs(pic1 - pic2) > (1 - self.seuil_hauteur) * max(pic1,pic2) :
            contaminant = min(pic1, pic2)
            pic_conta = self.foetus.data[marqueur]["Allele"][self.foetus.data[marqueur]["Hauteur"].index(contaminant)]
            # Test petit pic dans echo
            for pic_foetus in [pic, self.foetus.data[marqueur]["Allele"][self.foetus.data[marqueur]["Hauteur"].index(max(pic1, pic2))]]:
                if round(abs(pic_foetus - pic_conta),2) == 1.0:
                    self.foetus.data[marqueur]["conclusion"] = "Non informatif"
                    self.foetus.data[marqueur]["détails"] = "Echo"
                    break
                else:
                    self.foetus.data[marqueur]["conclusion"] = "Contaminé"
                    self.foetus.data[marqueur]["détails"] = round((contaminant / (contaminant + pic_pere)) * 100, 2)

        # Conta majeur
        else :
            self.foetus.data[marqueur]["conclusion"] = "Contaminé"
            self.foetus.data[marqueur]["détails"] = [round((pic1 / (pic1 + pic_pere)) * 100,2), round((pic2 / (pic2 + pic_pere)) * 100, 2)]
        
    def compute_homozygote_contamination(self, marqueur):
        # ajout echo si plus petit avant echo possible si apres conta
        if abs(self.foetus.data[marqueur]["Hauteur"][0] - self.foetus.data[marqueur]["Hauteur"][1]) > (1 - self.seuil_hauteur) * max(*self.foetus.data[marqueur]['Hauteur']) :
            contaminant = min(self.foetus.data[marqueur]["Hauteur"])
            autre = max(self.foetus.data[marqueur]["Hauteur"])
            # contaminant à n-1 du deuxieme pic donc echo 
            if round(abs(self.foetus.data[marqueur]["Allele"][0] - self.foetus.data[marqueur]["Allele"][1]),2) == 1.0 and self.foetus.data[marqueur]["Allele"][self.foetus.data[marqueur]["Hauteur"].index(contaminant)] < self.foetus.data[marqueur]["Allele"][self.foetus.data[marqueur]["Hauteur"].index(autre)]:
                self.foetus.data[marqueur]["conclusion"] = "Non informatif"
                self.foetus.data[marqueur]["détails"] = "Echo"
            else:
                self.foetus.data[marqueur]["détails"] = round(((2 * contaminant) / (contaminant + autre)) * 100, 2)
                self.foetus.data[marqueur]["conclusion"] = "Contaminé"
        else:
            self.foetus.data[marqueur]["conclusion"] = "Non informatif"
            self.foetus.data[marqueur]["détails"] = "Mêmes allèles que la mère"

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
                                "Concordance Pere/Foetus": [self.foetus.data[marqueur]["concordance"][1] for marqueur in
                                                            marqueurs], "Détails P/F": self.get_notconcordant(1)}
            else:
                resultat = {"Marqueur": marqueurs,
                            "Conclusion": [self.foetus.data[marqueur]["conclusion"] for marqueur in marqueurs],
                            "Détails M/F": [self.foetus.data[marqueur]["détails"] for marqueur in marqueurs]}
        else:
            if self.pere:
                if self.concordance_pere_foet:
                    resultat = {"Marqueur": marqueurs, "Concordance Mere/Foetus": [ self.foetus.data[marqueur]["concordance"][0] for marqueur in marqueurs ], "Détails M/F": self.get_notconcordant(0)}
                else:
                    resultat = {"Marqueur": marqueurs, "Concordance Mere/Foetus": [ self.foetus.data[marqueur]["concordance"][0] for marqueur in marqueurs ], "Détails M/F": self.get_notconcordant(0), "Concordance Pere/Foetus": [ self.foetus.data[marqueur]["concordance"][1] for marqueur in marqueurs ], "Détails P/F": self.get_notconcordant(1)}
            else:
                resultat = {"Marqueur": marqueurs, "Concordance Mere/Foetus": [ self.foetus.data[marqueur]["concordance"][0] for marqueur in marqueurs ], "Détails M/F": self.get_notconcordant(0)}
        return resultat

    def get_id(self):
        return self.foetus.ID

    def get_contamine(self):
        return self.contamine
        
    def get_conclusion(self):
        return self.conclusion
        
    
    def get_notconcordant(self, parent):
        """
        return the list of not concordant alleles
        parent: 0 for mother and 1 for father
        """
        list_alleles = []
        marqueurs = list(self.foetus.data)
        marqueurs.remove("AMEL")
        orig = "M: " if parent == 0 else "P: "
        for marqueur in marqueurs:
            if self.foetus.data[marqueur]["concordance"][parent] == "NON":
                val = str(self.mere.data[marqueur]["Allele"]) if parent == 0 else str(self.pere.data[marqueur]["Allele"])
                list_alleles.append(orig + val + " F: " + str(self.foetus.data[marqueur]["Allele"]))
            else:
                list_alleles.append("")
        return list_alleles

def allele_minus_one(self, marqueur, allele):
    return self.echelle[marqueur][self.echelle[marqueur].index(allele) - 1]

def common_element(list1,list2):
    list1_set = set(list1)
    list2_set = set(list2)
    #print(list1_set, list2_set, list1_set.intersection(list2_set))
    if len(list1_set.intersection(list2_set)) > 0:
        #print("alleles communs", list1_set.intersection(list2_set))
        return True
    return False

def get_echelle_allelique(self, path):
    echelle = {}
    with open(path, 'r') as FILE:
        lines = FILE.readlines()
    FILE.close()

    for num_line in range(0, len(lines), 2):
        echelle[lines[num_line]] = lines[num_line + 1]