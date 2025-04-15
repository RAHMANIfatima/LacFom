def lecture_fichier(path_data_frame):
    """
    Adaptation de la fonction lecture_fichier(path_data_frame) du fichier traitement.py pour l'application Django
    """
    data = []
    allsamples = []

    try:
        with open(path_data_frame, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return "ouverture impossible"

    if not lines:
        return "fichier vide"

    header = lines[0].strip().split('\t')
    if "Sample Name" not in header:
        return "colonne 'Sample Name' absente"


    for line in lines[1:]:
        cols = line.strip().split('\t')
        if len(cols) < len(header):
            cols+=[""]*(len(header)-len(cols))

        elif len(cols) > len(header):
            continue
        data.append(dict(zip(header, cols)))
    print("Lignes valides chargées :", len(data))

    if not data:
        return "aucune donnée valide"

    # sample_names = [row["Sample Name"] for row in data]

    #Check la présence de TPOS et NPOS
    # À ENLEVER AVEC LE FICHIER DE CONFIGURATION 
    # has_tpos = any("pos" in name.lower() for name in sample_names)
    # if not has_tpos:
    #     return "T POS absent"

    # has_tneg = any("neg" in name.lower() or "blanc" in name.lower() for name in sample_names)
    # if not has_tneg:
    #     return "T NEG absent"

    for row in data:
        name = row["Sample Name"].lower().strip()
        if "pos" in name:
            row["Sample Name"] = "TPOS"
        elif "neg" in name or "blanc" in name:
            row["Sample Name"] = "TNEG"

    allsamples = list(set(
        row["Sample Name"] for row in data if row["Sample Name"] not in ["TPOS", "TNEG"]
    ))

    # Check la présence de père
    if len(data) % 5 != 0 and len(data) % 4 != 0:
        return "Nombre de lignes incorrect"

    return [allsamples, data]
