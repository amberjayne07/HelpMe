from django.urls import path
from . import views

app_name = 'HelpMe_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about, name='about_us'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('login/', views.login, name='login'),
    path('post-overview/', views.post_overview, name='post_overview'),
]