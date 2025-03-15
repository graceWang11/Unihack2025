import requests
import json
import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from core.models import InterviewSession, User, SessionParticipant
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib import messages
from src.server import server
# ✅ Use credentials from settings.py (which now loads from .env)
try:
    EMAILJS_USER_ID = settings.EMAILJS_USER_ID
    EMAILJS_SERVICE_ID = settings.EMAILJS_SERVICE_ID
    EMAILJS_TEMPLATE_ID = settings.EMAILJS_TEMPLATE_ID
    EMAILJS_ENABLED = all([EMAILJS_USER_ID, EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID])
except AttributeError:
    EMAILJS_ENABLED = False
    print("EmailJS settings not found. Email notifications will be disabled.")

def home_view(request):
    """View for the home page, showing active and expired sessions."""
    # Get all sessions
    all_sessions = InterviewSession.objects.all().order_by('-start_time')
    
    active_sessions = []
    expired_sessions = []
    
    # Categorize sessions as active or expired
    for session in all_sessions:
        # Force update the session status
        session.update_status()
        
        if session.is_expired():
            session.is_active = False
            session.save()
            expired_sessions.append(session)
        elif session.is_active:
            active_sessions.append(session)
    
    # Limit expired sessions to the 5 most recent
    expired_sessions = expired_sessions[:5]
    
    # If this is an AJAX request, render just the sessions partial
    if request.GET.get('ajax') == '1':
        return render(request, 'core/partials/sessions_list.html', {
            'active_sessions': active_sessions,
            'expired_sessions': expired_sessions
        })
    
    return render(request, 'core/home.html', {
        'active_sessions': active_sessions,
        'expired_sessions': expired_sessions
    })

def room_view(request, id):
    """View for the interview room with shared editor and whiteboard."""
    print(f"Accessing room with ID: {id} (type: {type(id)})")
    
    try:
        # Try to get the session by ID
        session = InterviewSession.objects.get(id=id)
        print(f"Found session: {session.title}")
        
        # Check if session has expired
        if session.is_expired():
            print(f"Session {id} has expired")
            messages.error(request, "This session has expired and is no longer available.")
            return redirect('home')
        
        # Check if session is active
        if not session.is_active:
            # Update is_active based on current time
            now = timezone.now()
            if session.start_time <= now <= session.end_time:
                session.is_active = True
                session.save()
                print("Session activated")
            else:
                print("Session not active and outside time window")
                return redirect('home')
        
        # Check if a WebSocket room exists for this session, create one if not
        ws_room = server.get_room(id)
        if ws_room is None:
            print(f"Creating new WebSocket room for session {id}")
            room_id = server.new_room(str(id))
            print(f"Created WebSocket room with ID: {room_id}")
        
        # Render the room template with session info
        return render(request, 'core/room.html', {
            'room': id,
            'session': session
        })
    except InterviewSession.DoesNotExist:
        # If session doesn't exist, redirect to home
        print(f"No session found with ID: {id}")
        return redirect('home')
    except Exception as e:
        # Catch any other errors
        print(f"Error accessing room: {str(e)}")
        return redirect('home')

def send_access_code(session_id):
    session = get_object_or_404(InterviewSession, id=session_id)
    
    # Get participant emails
    participant_emails = list(session.participants.all().values_list('user__email', flat=True))
    all_recipients = [session.created_by.email] + participant_emails
    
    # Send email using Django's email system
    send_mail(
        subject=f"Interview Session: {session.title}",
        message=f"""
        Hi {session.created_by.username},
        
        Your interview session "{session.title}" has been created.
        Access code: {session.access_code}
        Start time: {session.start_time.strftime('%Y-%m-%d %H:%M')}
        
        This session will expire after 15 minutes.
        """,
        from_email="noreply@yourplatform.com",
        recipient_list=all_recipients,
        fail_silently=False,
    )
    print(f"✅ Email sent to {all_recipients}")

def create_session(request):
    """View to create a new interview session."""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        candidate_emails = request.POST.get("candidate_emails", "").split(",")
        candidate_emails = [email.strip() for email in candidate_emails if email.strip()]
        
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={'username': 'admin'}
        )
        
        # Set session start time to now
        start_time = timezone.now()
        
        # Create the session
        session = InterviewSession.objects.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=start_time + timezone.timedelta(minutes=15),  # 15 minute session
            created_by=admin_user
        )
        
        # Create a room in the WebSocket server with the same ID as the session
        room_id = server.new_room(str(session.id))
        print(f"Created WebSocket room with ID: {room_id}")
        
        # Add participants
        for email in candidate_emails:
            participant, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0]}
            )
            SessionParticipant.objects.create(
                session=session,
                user=participant
            )
        
        # Send email notification
        send_access_code(session.id)
        
        messages.success(request, f"Session '{title}' created successfully! Access code: {session.access_code}")
        return redirect('home')
    
    return render(request, 'core/create_session.html')

def join_session(request):
    """View to join an interview session using an access code."""
    if request.method == "POST":
        access_code = request.POST.get("access_code")
        confirm = request.POST.get("confirm")
        print(f"Attempting to join with access code: {access_code}, confirm={confirm}")
        
        # Check if confirm_join.html exists
        template_path = os.path.join(settings.BASE_DIR, 'core', 'templates', 'core', 'confirm_join.html')
        if not os.path.exists(template_path):
            print(f"WARNING: Template file {template_path} does not exist!")
        
        # Try to find the session with this access code
        try:
            session = InterviewSession.objects.get(access_code=access_code)
            print(f"Found session: {session.id} - {session.title}")
            
            # Check if session has expired
            if session.is_expired():
                print(f"Session {session.id} has expired")
                return render(request, "core/home.html", {
                    "error": "This session has expired and is no longer available.",
                    "access_code": access_code
                })
            
            # Check if session is active
            if not session.is_active:
                # Update is_active based on current time
                now = timezone.now()
                if session.start_time <= now <= session.end_time:
                    session.is_active = True
                    session.save()
                    print("Session activated")
                else:
                    print("Session not active and outside time window")
                    return render(request, "core/home.html", {
                        "error": "This session is not active yet or has expired.",
                        "access_code": access_code
                    })
            
            # If not confirmed yet, show confirmation page
            if not confirm or confirm != "1":
                print("Showing confirmation page")
                return render(request, "core/confirm_join.html", {
                    "session": session,
                    "access_code": access_code
                })
            
            # Redirect to the room view with the session ID
            print(f"Confirmed! Redirecting to room/{session.id}/")
            return redirect('room', id=session.id)
            
        except InterviewSession.DoesNotExist:
            print(f"No session found with access code: {access_code}")
            # List all access codes in the database for debugging
            all_codes = InterviewSession.objects.values_list('access_code', flat=True)
            print(f"Available access codes: {list(all_codes)}")
            return render(request, "core/home.html", {
                "error": "Invalid access code. Please try again.",
                "access_code": access_code
            })
    
    return redirect('home')