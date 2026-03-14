from django import forms
from HelpMe_app.models import *

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['full_name', 'username', 'dateOfBirth', 'email', 'password']