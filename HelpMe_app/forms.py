from django import forms
from django.contrib.auth.forms import UserCreationForm
from HelpMe_app.models import *

class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Alistair Morrison'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'e.g. alistairmorrison123@email.com'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g. alistair_m'})
    )
    dateOfBirth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    passwordHint = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Password hint'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("full_name", "username", "email", "dateOfBirth", "passwordHint", "picture")

    def save(self, commit=True):
        user = super().save(commit=False)

        # All new users are STANDARD unless otherwise created (e.g. through admin or anonymous users).
        user.type = User.STANDARD
        if commit:
            user.save()
        return user