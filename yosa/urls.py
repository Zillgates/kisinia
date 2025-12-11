from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='yosa/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Events
    path('events/', views.events_list, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', views.register_event, name='register_event'),
      path('past-events/', views.past_events, name='past_events'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

        path('messages/', views.messages_list, name='messages'),
    path('messages/send/', views.send_message, name='send_message'),
    path('feedback/', views.send_feedback, name='send_feedback'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    
    # Feedback
    path('feedback/', views.send_feedback, name='send_feedback'),
]