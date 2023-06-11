from django import forms
from .models import Color

class ColorForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    color = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Color
        fields = ['name', 'image', 'color']
