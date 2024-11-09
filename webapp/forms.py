from django import forms

class CodeForm(forms.Form):
    access_code = forms.CharField(max_length=8, label="Ingrese el código de acceso")
