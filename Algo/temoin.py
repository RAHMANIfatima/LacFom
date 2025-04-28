
from individus import Individus

class Temoin(Individus):
    """ Common informations between mother, fetus and father

        Attributes :
            data (dict) : markers, alleles, heights and informatif character
    """

    def __init__(self, ID, data, kit):
        """ The constructor for Patient class

            Parameters :
            ID (str) : name
            genre (str) ["pos", "neg"] : type of 
            data (dict)
        """
        super().__init__(ID, data)
        self.kit = kit
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
        listeFalse = []
        for marqueur in self.TPOS.keys():
            if (self.ispositif and self.data[marqueur]['Allele'] != self.TPOS[marqueur]) or (not self.ispositif and self.data[marqueur]['Allele'] != []) :
                listeFalse.append(marqueur)
            elif self.ispositif == 6:
                #sys.out.write("Error: name for positive/negative control is unknown")
                return self.ispositif
        return listeFalse




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