from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

app_name = 'HelpMe_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about, name='about_us'),

    path('join_us/', views.account_upsell, name='account_upsell'),
    path('back/', views.go_back, name='go_back'),

    # AUTHENTICATION
    path('sign-up/', views.sign_up, name='sign_up'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('my-account/', views.my_account, name='my_account'),

    path('test-everything/', views.test_everything, name='test_everything'),

    # RESPONDING TO POSTS
    path('post/<uuid:question_id>/', views.post_overview, name='post_overview'),
    path('post/<uuid:question_id>/like/', views.like_question, name='like_question'),
    path('post/<uuid:question_id>/comment/', views.create_comment, name='create_comment'),
    path('respond-to-suggestion/<uuid:item_id>/', views.respond_to_suggestion, name='respond_to_suggestion'),

    path('vote/<uuid:item_id>/', views.vote_on_poll, name='vote_on_poll'),

    # POST CREATION / EDITING TOOLS
    path('create/', views.create_question, name='create_question'),
    path('post/<uuid:question_id>/edit/', views.edit_question, name='edit_question'),
    path('post/<uuid:question_id>/delete/', views.delete_question, name='delete_question'),

    # NOTIFICATIONS
    path('notifications/mark-read/<uuid:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/clear-history/', views.clear_notification_history, name='clear_notification_history'),

    # ADMIN ONLY
    path('category/create/', views.create_category, name='create_category'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)