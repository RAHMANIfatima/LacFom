from django.shortcuts import render

# from Algo.echantillon import echantillon
# from Algo.individus import individus
# from Algo.foetus import foetus
# from Algo.mere import mere
# from Algo.pere import pere
# from Algo.temoin import temoin


def afficher_importation(request):
    contenu = request.session.pop("contenu_fichier", None)  # Récupère le contenu et le supprime après affichage
    return render(request, "analyse/identification.html", {"contenu": contenu})

def traiter_choix(request):
    samples=request.session.get("samples")
    data=request.session.get("data")
    # print(f"Longueur de samples2 : {len(samples)}")
    # print(f"Longueur de data2 : {len(data)}")
    
    if len(samples)==3:
        print("Présence d'un père")
        return render(request,"analyse/identification_avec_pere.html",{
                      "samples":samples,
                      "data":data,
        })
    
    print("Absence de père")
    return render(request, "analyse/identification.html", {
                      "samples":samples,
                      "data":data,
    })
