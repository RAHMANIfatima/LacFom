from individus import Individus

class Foetus(Individus):
    """ Function exclusive to foetus
    """
    def __init__(self, ID, data):
        Individus.__init__(self, ID, data)

    def get_sexe(self):
        for marqueur in self.data.keys():
            if 'Y' in self.data[marqueur]['Allele']:
                return 'M'
        return 'F'
