
from Algo.individus import Individus


class Temoin(Individus):
    """ Common informations between mother, fetus and father

        Attributes :
            data (dict) : markers, alleles, heights and informatif character
    """

    def __init__(self, ID, data):
        """ The constructor for Patient class

            Parameters :
            ID (str) : name
            genre (str) ["pos", "neg"] : type of 
            data (dict)
        """
        super().__init__(ID, data)
        self.ispositif = self.det_genre()
        self.TPOS = {"AMEL":["X","Y"], "CSF1PO":[12],"D13S317":[9,11],"D16S539":[9,13], "D18S51":[16,18], "D21S11":[29,31.2], "D3S1358":[17,18], "D5S818":[12],"D7S820":[8,11], "D8S1179":[14,15], "FGA":[20,23], "Penta_D":[12,13], "Penta_E":[7,14], "TH01":[6,9.3], "TPOX":[11], "vWA":[16,19]} #2800M

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
