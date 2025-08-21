from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('room/<int:user_id>/', views.get_or_create_chatroom, name='chat_room'),
    path('send/<int:room_id>/', views.send_message, name='send_message'),
    path('messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('unread_counts/', views.get_unread_counts, name='unread_counts'),  # Add this line
    path('update_status/', views.update_user_status, name='update_status'),
    path('user_status/<int:user_id>/', views.get_user_status, name='user_status'),
]