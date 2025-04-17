import json
from pathlib import Path

def load_kits():
    chemin_fichier = Path(__file__).resolve().parent / 'deafault-marker.json'
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        donnees = json.load(f)
        return donnees

def save_kits(kits):
    chemin_fichier = Path(__file__).resolve().parent / 'deafault-marker.json'
    with open(chemin_fichier, 'w', encoding='utf-8') as f:
        json.dump(kits, f, ensure_ascii=False, indent=4)

def get_kits():
    kits = load_kits()
    return list(kits.keys())