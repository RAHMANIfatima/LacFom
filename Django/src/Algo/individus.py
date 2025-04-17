class Individus:
    """ Common informations between mother, fetus and father

        Attributes :
            data (dict) : markers, alleles, heights and informatif character
    """

    def __init__(self, ID, data):
        """ The constructor for Patient class

            Parameters :
            ID (str) : name
            data (dict)
        """
        self.ID = ID
        self.data = data


    def get_ID(self):
        return self.ID