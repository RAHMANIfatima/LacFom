import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import Image, Table, TableStyle, Paragraph
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
import re

from .echantillon import *

def head_page(entite, emetteur, version, date):
    """
    Define the head of the report and it's content
    entite : lab localisation
    emetteur : laboratory
    version : tool version
    echantillon.date : date of the analysis of the echantillon
    """
    styles = getSampleStyleSheet()
    style = styles["Normal"]

    CHU= Image(os.path.join('logo_chu.png'))
    CHU.drawHeight = 3.18 * cm * CHU.drawHeight / CHU.drawWidth
    CHU.drawWidth = 3.25 * cm

    entite = Paragraph("<font size=12><b>Entité d'application :</b> " + entite + "</font>", style)
    emetteur = Paragraph("<font size=12><b>Emetteur :</b>" + emetteur + " </font>", style)
    no_version = Paragraph("<font size=12><b>LACFoM v" + version + "</b></font>", style)
    doc = Paragraph("<para align=center spaceb=3><font size=12>DOCUMENT D’ENREGISTREMENT</font></para>", style)
    page = Paragraph("<font size=12>Page : 1/1</font>", style)
    chu_titre = Paragraph("<para align=center spaceb=3><b><font size=15><font color=white>Feuille de résultats Recherche de contamination maternelle Kit PowerPlex 16 ® </font></font></b></para>", styles["Title"])

    chu_tab = [[CHU, [entite, emetteur], "", "", "", no_version],
               ["", doc, "", "", "", page],
               [chu_titre, "", "", "", "", ""]]
    if Concordance_pf == "NON" or Concordance_mf == "NON":
        CHU_HEADER = Table(chu_tab, colWidths=3.4 * cm, rowHeights=1 * cm)
    else:
        CHU_HEADER = Table(chu_tab, colWidths=4.65 * cm, rowHeights=1 * cm)
    CHU_HEADER.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.black),
                                ('SPAN', (1, 0), (4, 0)),
                                ('SPAN', (1, 1), (4, 1)),
                                ('SPAN', (0, 2), (5, 2)),
                                ('SPAN', (0, 0), (0, 1)),
                                ('BACKGROUND', (0, 2), (5, 2), colors.lightgrey),
                                ('VALIGN', (1, 0), (3, 2), 'MIDDLE'),
                                ('VALIGN', (4, 0), (5, 1), 'MIDDLE'),
                                ('ALIGN', (0, 0), (3, 2), 'CENTER'),
                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
    return CHU_HEADER

def title():
    """
    Define the title of the analysis report
    """

def table_mother_not_concordant():
    """
    Define the table for not concordant data with the mother
    """
    pass

def table_father_not_concordant():
    """
    Define the table for not concordant dna with father and contamination analysis
    """
    pass

def table_analysis():
    """
    Define the table for the analysis
    """
    pass

def report(output_path, echantillon, conclusion, choix, user, seuil_hauteur_pic, seuil_nb_marqueur, seuil_percent_conta_, tpos, tneg, entite, emetteur, version):
    """
    Define and create the pdf report for the analysis
    Input:
      path : path of the pdf
      echantillon (object): Echantillon object of the analysis
      conclusion (int) : Code value of the conclusion of the analysis
      user (str) : user name
      seuil_hauteur_pic (int) : Threshold used to decide if a signal should be considered as a contamination
      seuil_nb_marqueur (int) : Threshold used to decide the minimal number of contaminated marker needed to conclude on a contamination
      seuil_percent_conta (float) : Threshold for the minimal percentage to decide if a sample is contaminated as a whole
      tpos (bool) : indicates if the tpos is ok
      tneg (bool) : indicates if the tneg is ok
      entite (string) : sharepoint quality data
      emetteur (string) : sharepoint quality data
      version (string) : version of the software
    """
    # Determination si portrait ou paysage
    if not echantillon.concordance_pere_foet:
        if not echantillon.concordance_mere_foet:
            # feuille verticale
            canv = Canvas(output_path, pagesize=A4)
        else:
            # feuille horizontale avec tableau dedouble
            canv = Canvas(output_path, pagesize=landscape(A4))
    else:
        # feuille horizontale
        canv = Canvas(output_path, pagesize=A4)

    CHU_HEADER = Table(chu_tab,colWidths=3.4*cm, rowHeights=1*cm)

    head = head_page(entite, emetteur, version, echantillon.date)

    """
    ##Variables
    elements = []

    # On créé le tableau
    data = [['1-a', '2-a', '3-a', '4-a', '5-a'],
            ['1-b', '2-b', '3-b', '4-b', '5-b'],
            ['1-c', '2-c', '3-c', '4-c', '5-c'],
            ['1-d', '2-d', '3-d', '4-d', '5-d']]

    t = Table(data)
    t.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))

    # Création du style h1 (titre n°1)
    h1 = PS(
        name='Heading1',
        fontSize=14,
        leading=16)

    # Création du paragraphe
    elements.append(Paragraph("Grand titre", h1))

    # On créé la page vierge
    doc = SimpleDocTemplate("form.pdf", pagesize=A4)
    # On ajoute le tableau
    elements.append(t)
    doc.build(elements)
    """