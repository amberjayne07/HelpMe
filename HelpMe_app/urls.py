from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from helpme_project import settings
from . import views

app_name = 'HelpMe_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about, name='about_us'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('login/', views.login, name='login'),
    path('my-account/', views.my_account, name='my_account'),
    path('test-everything/', views.test_everything, name='test_everything'),
    path('post/<uuid:question_id>/', views.post_overview, name='post_overview'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)