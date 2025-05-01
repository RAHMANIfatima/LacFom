
from Algo.individus import Individus
from Algo.kit import Kit

class Temoin(Individus):
    """ Common informations between mother, fetus and father

        Attributes :
            data (dict) : markers, alleles, heights and informatif character
    """

    def __init__(self, ID, data, kit=None):
        """ The constructor for Patient class

            Parameters :
            ID (str) : name
            genre (str) ["pos", "neg"] : type of 
            data (dict)
        """
        super().__init__(ID, data)
        kitObject = Kit(kit)
        self.kit = kitObject
        self.ispositif = self.det_genre()
        self.TPOS = self.kit.get_tpos_data()  # récupération dynamique du profil TPOS

    def det_genre(self):
        if "POS" in self.ID.upper():
            return True
        elif "NEG" in self.ID.upper():
            return False
        else:
            # Ni temoin positif ni negatif ... probleme
            return 6





    def check(self):
        """Vérifie la concordance entre les données du témoin et les valeurs attendues."""
        if self.ispositif == 6:
            return self.ispositif

        listeFalse = []
        for marqueur in self.TPOS.keys():
            allele_observe = self.data.get(marqueur, {}).get('Allele', [])

            if self.ispositif and allele_observe != self.TPOS[marqueur]:
                listeFalse.append(marqueur)
            elif not self.ispositif and allele_observe != []:
                listeFalse.append(marqueur)

        return listeFalse                