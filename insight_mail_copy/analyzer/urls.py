from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'), # Default to login
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    path('inbox/', views.dashboard, name='dashboard'),
    path('sent/', views.sent_box, name='sent_box'),
    path('compose/', views.compose_email, name='compose_email'),
    
    path('email/<int:email_id>/', views.email_detail, name='email_detail'),
    path('analyze/<int:email_id>/', views.analyze_email, name='analyze_email'),
    path('sync-gmail/', views.sync_gmail_view, name='sync_gmail'),
]