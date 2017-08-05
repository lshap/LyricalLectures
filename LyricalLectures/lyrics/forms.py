from django import forms

class PresentationForm(forms.Form):
    presentation_url = forms.CharField(label="Presentation link", max_length=300)
