from http.client import HTTPResponse

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def post_overview(request):
    return render(request, 'post_overview.html')
def about(request):
    return render(request, 'about_us.html')

def sign_up(request):
    return render(request, 'authentication/sign_up.html')

def login(request):
    return render(request, 'authentication/login.html')