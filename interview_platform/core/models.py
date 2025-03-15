from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class InterviewSession(models.Model):
    """Model representing an interview session that users can join."""
    # Session title and description
    title = models.CharField(max_length=200, default="Interview Session")
    description = models.TextField(blank=True, null=True)
    
    # Session timing
    start_time = models.DateTimeField(help_text="When the session becomes active")
    end_time = models.DateTimeField(help_text="When the session expires")
    date_created = models.DateTimeField(default=timezone.now)
    
    # Session status is calculated based on current time vs start/end times
    is_active = models.BooleanField(default=False)
    
    # Access code for joining the session
    access_code = models.CharField(max_length=10, unique=True)
    
    # Additional settings
    max_participants = models.PositiveIntegerField(default=10)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    
    def __str__(self):
        if self.is_active:
            return f"ACTIVE SESSION: {self.start_time.strftime('%Y-%m-%d')}"
        elif timezone.now() < self.start_time:
            return f"UPCOMING SESSION: {self.start_time.strftime('%Y-%m-%d')}"
        else:
            return f"EXPIRED SESSION: {self.start_time.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Generate a random access code if not provided
        if not self.access_code:
            self.access_code = str(uuid.uuid4())[:8].upper()
            
        # Update is_active based on current time
        now = timezone.now()
        self.is_active = (self.start_time <= now <= self.end_time)
        
        super().save(*args, **kwargs)
    
    @property
    def status(self):
        """Returns the current status of the session."""
        now = timezone.now()
        if now < self.start_time:
            return "upcoming"
        elif now <= self.end_time:
            return "active"
        else:
            return "expired"
    
    def update_status(self):
        """Update the is_active status based on current time."""
        now = timezone.now()
        old_status = self.is_active
        self.is_active = (self.start_time <= now <= self.end_time)
        if old_status != self.is_active:
            self.save(update_fields=['is_active'])
        return self.is_active
    
    class Meta:
        ordering = ['-start_time']


class SessionParticipant(models.Model):
    """Model representing a participant in an interview session."""
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_participations')
    join_time = models.DateTimeField(default=timezone.now)
    is_present = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('session', 'user')
        
    def __str__(self):
        return f"{self.user.username} in {self.session}"


class SessionCode(models.Model):
    """Model specifically for tracking access codes and their usage."""
    code = models.CharField(max_length=10, unique=True)
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='session_code')
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Code: {self.code} for {self.session}"