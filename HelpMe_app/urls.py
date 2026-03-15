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

    # RESPONDING TO POSTS.
    path('post/<uuid:question_id>/like/', views.like_question, name='like_question'),

    # NOTIFICATIONS.
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/clear-history/', views.clear_notification_history, name='clear_notification_history'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
