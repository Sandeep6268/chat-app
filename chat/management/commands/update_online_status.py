from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from chat.models import UserProfile

class Command(BaseCommand):
    help = 'Mark users as offline if they were last seen more than 5 minutes ago'
    
    def handle(self, *args, **options):
        # Mark users as offline if they were last seen more than 5 minutes ago
        offline_threshold = timezone.now() - timedelta(minutes=5)
        
        # Update users who are marked as online but haven't been seen recently
        inactive_profiles = UserProfile.objects.filter(
            is_online=True,
            last_seen__lt=offline_threshold
        )
        
        count = inactive_profiles.update(is_online=False)
        
        self.stdout.write(self.style.SUCCESS(f'Marked {count} users as offline'))