from individus import Individus

class Mere(Individus):
    """ Exclusive informations about the mother. Mere class inherits from Patient.
    """

    def __init__(self, ID, data):
        """ """
        # On appelle explicitement le constructeur de Personne :
        Individus.__init__(self, ID, data)
        

    
    def check_sex(self):
        for marqueur in self.data.keys():
            if 'Y' in self.data[marqueur]['Allele']:
                return False
        return True