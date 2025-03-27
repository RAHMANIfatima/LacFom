from individus import Individus

class Pere(Individus):
    """ Exclusive informations about the father. Pere class inherits from Patient.

        Did not implement because mother and fetus are enough to conclude.
    """
    def __init__(self, ID, data):
        """ """
        # On appelle explicitement le constructeur de Personne :
        Individus.__init__(self, ID, data)

    def check_sex(self):
        for marqueur in self.data.keys():
            if 'Y' in self.data[marqueur]['Allele']:
                return True
        return False
