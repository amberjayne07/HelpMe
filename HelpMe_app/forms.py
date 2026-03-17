from django import forms
from django.contrib.auth.forms import UserCreationForm
from HelpMe_app.models import *


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. Alistair Morrison'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'e.g. alistair@glasgow.ac.uk'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. alistairloveshelpme'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    password_hint = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Password hint'}))
    picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("full_name", "username", "email", "date_of_birth", "password_hint", "picture")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.type = User.STANDARD

        user.full_name = self.cleaned_data.get('full_name')
        user.email = self.cleaned_data.get('email')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        user.password_hint = self.cleaned_data.get('password_hint')
        user.picture = self.cleaned_data.get('picture')

        if commit:
            user.save()
        return user

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'category_id', 'description']