from django import forms

class UploadFileForm(forms.Form):
    fichier = forms.FileField(label="Sélectionnez un fichier TXT")
