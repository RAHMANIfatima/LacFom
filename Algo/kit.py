import json

class Kit:
    """Classe représentant un kit de marqueurs génétiques."""

    def __init__(self, name, json_path):
        """
        Initialise un objet Kit avec un nom et le chemin du fichier JSON contenant les données du TPOS.

        :param name: Nom du kit (str)
        :param json_path: Chemin vers le fichier JSON (str)
        """
        self.name = name
        self.json_path = json_path
        self.tpos_data = self.load_data()

    def load_data(self):
        """Charge les données du fichier JSON et les stocke dans un dictionnaire."""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("TPOS", {})  # on accède directement aux données du témoin positif
        except FileNotFoundError:
            print(f"Erreur : fichier JSON introuvable à l'emplacement : {self.json_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Erreur : le fichier JSON {self.json_path} est invalide.")
            return {}
        
    def get_nb_marqueurs(self):
        """"Retourne le nombre de marqueurs présents dans le kit de TPOS."""""
        return len(self.tpos_data)


    def get_tpos_data(self):
        """Retourne les données du témoin positif."""
        return self.tpos_data

    def get_marqueurs(self):
        """Retourne la liste des marqueurs présents dans le kit."""
        return list(self.tpos_data.keys())
