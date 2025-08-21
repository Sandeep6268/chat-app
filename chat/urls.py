from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('chat/register/', views.register_view, name='register'),
    path('chat/login/', views.login_view, name='login'),
    path('chat/logout/', views.logout_view, name='logout'),
    path('chat/room/<int:user_id>/', views.get_or_create_chatroom, name='chat_room'),
    path('chat/send/<int:room_id>/', views.send_message, name='send_message'),
    path('chat/messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('chat/unread_counts/', views.get_unread_counts, name='unread_counts'),  # Add this line
    path('chat/update_status/', views.update_user_status, name='update_status'),
    path('chat/user_status/<int:user_id>/', views.get_user_status, name='user_status'),
]