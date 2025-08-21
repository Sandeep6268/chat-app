from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import UserRegisterForm, MessageForm
from .models import ChatRoom, Message
import json

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat')
    else:
        form = UserRegisterForm()
    return render(request, 'chat/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat')
        else:
            return render(request, 'chat/login.html', {'error': 'Invalid credentials'})
    return render(request, 'chat/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# In your views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import UserRegisterForm, MessageForm
from .models import ChatRoom, Message, UserMessageStatus
import json

@login_required
def chat_view(request):
    users = User.objects.exclude(id=request.user.id)
    
    # Get unread message counts for each user
    user_data = []
    for user in users:
        # Get or create chat room between current user and this user
        user_ids = sorted([request.user.id, user.id])
        room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        
        chat_room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            defaults={'is_group': False}
        )
        
        # Add participants if not already added
        if request.user not in chat_room.participants.all():
            chat_room.participants.add(request.user)
        if user not in chat_room.participants.all():
            chat_room.participants.add(user)
        
        # Count unread messages from this user
        unread_count = Message.objects.filter(
            room=chat_room, 
            sender=user,
            read=False
        ).exclude(sender=request.user).count()
        
        # Get last message preview
        last_message = Message.objects.filter(room=chat_room).order_by('-timestamp').first()
        last_message_preview = last_message.content if last_message else "No messages yet"
        
        user_data.append({
            'user': user,
            'unread_count': unread_count,
            'last_message': last_message_preview
        })
    
    return render(request, 'chat/chat.html', {'user_data': user_data})

# Add this to update user online status
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import UserRegisterForm, MessageForm
from .models import ChatRoom, Message, UserProfile
import json
@login_required
def update_user_status(request):
    if request.method == 'POST':
        is_online = json.loads(request.POST.get('is_online', 'false'))
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.is_online = is_online
        if not is_online:
            profile.last_seen = timezone.now()
        profile.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

# Update the get_or_create_chatroom view to mark messages as read
@login_required
def get_or_create_chatroom(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Create a unique room name by combining user IDs in sorted order
    user_ids = sorted([request.user.id, other_user.id])
    room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
    
    # Get or create the chat room
    chat_room, created = ChatRoom.objects.get_or_create(
        name=room_name,
        defaults={'is_group': False}
    )
    
    # Add participants if not already added
    if request.user not in chat_room.participants.all():
        chat_room.participants.add(request.user)
    if other_user not in chat_room.participants.all():
        chat_room.participants.add(other_user)
    
    # Mark all messages from this user as read and set read timestamp
    messages = Message.objects.filter(
        room=chat_room, 
        sender=other_user,
        read=False
    )
    
    for message in messages:
        message.read = True
        message.read_timestamp = timezone.now()  # Set read timestamp
        message.save()
    
    messages = Message.objects.filter(room=chat_room).order_by('timestamp')[:100]
    
    # UTC time mein +5:30 add karo
    for message in messages:
        ist_timestamp = add_ist_offset(message.timestamp)
        message.formatted_time = ist_timestamp.strftime('%I:%M %p')
        
        if message.read_timestamp:
            ist_read_timestamp = add_ist_offset(message.read_timestamp)
            message.formatted_read_time = ist_read_timestamp.strftime('%I:%M %p')
    # Get updated user data for sidebar
    users = User.objects.exclude(id=request.user.id)
    user_data = []
    for user in users:
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Calculate last seen text
        if profile.is_online:
            status_text = "Online"
        else:
            # Calculate time ago
            now = timezone.now()
            diff = now - profile.last_seen
            if diff.days > 0:
                status_text = f"Last seen {diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                status_text = f"Last seen {hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                status_text = f"Last seen {minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                status_text = "Last seen just now"
        
        # Get or create chat room between current user and this user
        user_ids = sorted([request.user.id, user.id])
        user_room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        
        user_chat_room, created = ChatRoom.objects.get_or_create(
            name=user_room_name,
            defaults={'is_group': False}
        )
        
        # Count unread messages from this user
        unread_count = Message.objects.filter(
            room=user_chat_room, 
            sender=user
        ).exclude(read_by=request.user).count()
        
        # Get last message preview
        last_message = Message.objects.filter(room=user_chat_room).order_by('-timestamp').first()
        last_message_preview = last_message.content if last_message else "No messages yet"
        
        user_data.append({
            'user': user,
            'unread_count': unread_count,
            'last_message': last_message_preview,
            'is_online': profile.is_online,
            'status_text': status_text
        })
    
    return render(request, 'chat/room.html', {
        'room': chat_room,
        'other_user': other_user,
        'messages': messages,
        'user_data': user_data
    })

# Add a view to get user status
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import UserProfile
from django.utils import timezone
from datetime import datetime

@login_required
def get_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Calculate time difference if user is offline
    status_info = {
        'is_online': profile.is_online,
    }
    
    if not profile.is_online:
        now = timezone.now()
        diff = now - profile.last_seen
        
        if diff.days > 0:
            status_info['last_seen'] = f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            status_info['last_seen'] = f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            status_info['last_seen'] = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            status_info['last_seen'] = "just now"
    else:
        status_info['last_seen'] = None
    
    return JsonResponse(status_info)
# views.py
from datetime import timedelta

def add_ist_offset(timestamp):
    """UTC time mein +5:30 hours add karta hai"""
    return timestamp + timedelta(hours=5, minutes=30)
@login_required
def send_message(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(ChatRoom, id=room_id)
        content = request.POST.get('content')
        
        if content:
            message = Message.objects.create(
                room=room,
                sender=request.user,
                content=content
            )
            
            # UTC time mein +5:30 add karo
            ist_timestamp = add_ist_offset(message.timestamp)
            formatted_time = ist_timestamp.strftime('%I:%M %p')
            
            return JsonResponse({
                'status': 'success',
                'message': message.content,
                'sender': message.sender.username,
                'timestamp': message.timestamp.isoformat(),
                'formatted_time': formatted_time
            })
    
    return JsonResponse({'status': 'error'})

# views.py
from django.utils.timezone import localtime

@login_required
def get_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = Message.objects.filter(room=room).order_by('timestamp')
    
    messages_data = []
    for msg in messages:
        # UTC time mein +5:30 add karo
        ist_timestamp = add_ist_offset(msg.timestamp)
        formatted_time = ist_timestamp.strftime('%I:%M %p')
        
        formatted_read_time = None
        if msg.read_timestamp:
            ist_read_timestamp = add_ist_offset(msg.read_timestamp)
            formatted_read_time = ist_read_timestamp.strftime('%I:%M %p')
        
        messages_data.append({
            'sender': msg.sender.username,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'formatted_time': formatted_time,
            'is_me': msg.sender == request.user,
            'read': msg.read,
            'read_timestamp': msg.read_timestamp.isoformat() if msg.read_timestamp else None,
            'formatted_read_time': formatted_read_time
        })
    
    return JsonResponse({'messages': messages_data})

# Add this view to your views.py
@login_required
def update_seen_status(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(ChatRoom, id=room_id)
        message_content = request.POST.get('message_content')
        
        if message_content:
            # Find the message
            message = Message.objects.filter(
                room=room, 
                content=message_content
            ).order_by('-timestamp').first()
            
            if message:
                # Add current user to read_by
                message.read_by.add(request.user)
                
                # If all participants have read the message, mark as read
                if message.read_by.count() == room.participants.count() - 1:  # Excluding sender
                    message.read = True
                    message.save()
                
                return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'})

# Add this new view to get unread counts
@login_required
def get_unread_counts(request):
    users = User.objects.exclude(id=request.user.id)
    unread_data = {}
    
    for user in users:
        # Get chat room between current user and this user
        user_ids = sorted([request.user.id, user.id])
        room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        
        chat_room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            defaults={'is_group': False}
        )
        
        # Count unread messages from this user
        unread_count = Message.objects.filter(
            room=chat_room, 
            sender=user,
            read=False
        ).exclude(sender=request.user).count()
        
        unread_data[user.id] = unread_count
    
    return JsonResponse(unread_data)