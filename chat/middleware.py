# In middleware.py
import time
from django.utils import timezone
from .models import UserProfile

class OnlineStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.is_online = True
                profile.last_seen = timezone.now()
                profile.save()
            except Exception as e:
                # Log error but don't break the request
                print(f"Error updating user status: {e}")
                
        response = self.get_response(request)
        return response