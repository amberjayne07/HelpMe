from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import views

app_name = 'HelpMe_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about, name='about_us'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('login/', views.login, name='login'),

    path('logout/', views.logout, name='logout'),

    path('change-password/', views.change_password, name='change_password'),
    path('my-account/', views.my_account, name='my_account'),
    path('test-everything/', views.test_everything, name='test_everything'),
    path('post/<uuid:question_id>/', views.post_overview, name='post_overview'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
