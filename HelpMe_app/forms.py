from django import forms
from django.contrib.auth.forms import UserCreationForm
from HelpMe_app.models import *


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. Alistair Morrison'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'e.g. alistair@glasgow.ac.uk'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. alistairloveshelpme'}))
    dateOfBirth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    passwordHint = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Password hint'}))
    picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("full_name", "username", "email", "dateOfBirth", "passwordHint", "picture")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.type = User.STANDARD
        if commit:
            user.save()
        return user
