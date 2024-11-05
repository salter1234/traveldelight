from django import forms
from .models import Subscriber2

class EmailForm(forms.ModelForm):
    class Meta:
        model = Subscriber2
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your E-mail Address'})
        }