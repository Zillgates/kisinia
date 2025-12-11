from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import User, Event, Registration, Message, Trending
from .forms import (CustomUserCreationForm, UserUpdateForm, 
                    EventRegistrationForm, MessageForm, FeedbackForm,EventForm)

def home(request):
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now(),
        is_active=True
    ).order_by('date')[:3]
    
    trending_events = Trending.objects.select_related('event').filter(
        event__date__gte=timezone.now()
    ).order_by('-views')[:3]
    
    context = {
        'upcoming_events': upcoming_events,
        'trending_events': [t.event for t in trending_events],
    }
    return render(request, 'yosa/home.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'yosa/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    registrations = Registration.objects.filter(
        user=user, 
        status='confirmed'
    ).select_related('event')
    
    upcoming_registrations = registrations.filter(event__date__gte=timezone.now())
    past_registrations = registrations.filter(event__date__lt=timezone.now())
    
    # Update trending views
    for reg in upcoming_registrations:
        trending, created = Trending.objects.get_or_create(event=reg.event)
        trending.views += 1
        trending.save()
    
    # Count friends registered
    friends_count = Registration.objects.filter(
        event__date__gte=timezone.now()
    ).exclude(user=user).count()
    
    # Upcoming events
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now(),
        is_active=True
    ).exclude(
        id__in=registrations.values_list('event_id', flat=True)
    ).order_by('date')[:5]
    
    # Trending events
    trending = Trending.objects.select_related('event').filter(
        event__date__gte=timezone.now()
    ).order_by('-views')[:5]
    
    context = {
        'user': user,
        'upcoming_registrations': upcoming_registrations,
        'past_registrations': past_registrations,
        'friends_count': friends_count,
        'upcoming_events': upcoming_events,
        'trending_events': [t.event for t in trending],
    }
    return render(request, 'yosa/dashboard.html', context)

@login_required
def events_list(request):
    events = Event.objects.filter(
        date__gte=timezone.now(),
        is_active=True
    ).order_by('date')
    return render(request, 'yosa/events.html', {'events': events})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_registered = Registration.objects.filter(
        user=request.user, 
        event=event, 
        status='confirmed'
    ).exists()
    
    # Update trending clicks
    trending, created = Trending.objects.get_or_create(event=event)
    trending.clicks += 1
    trending.save()
    
    return render(request, 'yosa/event_detail.html', {
        'event': event,
        'user_registered': user_registered,
        'seats_left': event.seats_left(),
    })

@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.event = event
            
            if event.seats_left() > 0:
                registration.save()
                event.current_attendees += 1
                event.save()
                messages.success(request, f'Successfully registered for {event.title}!')
            else:
                messages.error(request, 'Sorry, this event is full.')
            
            return redirect('dashboard')
    else:
        form = EventRegistrationForm()
    
    return render(request, 'yosa/register_event.html', {
        'event': event,
        'form': form,
    })

@login_required
def profile(request):
    user = request.user
    registrations = Registration.objects.filter(user=user).count()
    
    context = {
        'user': user,
        'registrations_count': registrations,
    }
    return render(request, 'yosa/profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'yosa/update_profile.html', {'form': form})

@login_required
def send_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.is_feedback = True
            message.save()
            messages.success(request, 'Feedback sent successfully!')
            return redirect('dashboard')
    else:
        form = FeedbackForm()
    
    return render(request, 'yosa/send_feedback.html', {'form': form})

# Add more views for messages, admin features, etc.
# Add these missing views to your existing views.py

@login_required
def cancel_registration(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration = get_object_or_404(
        Registration, 
        user=request.user, 
        event=event,
        status='confirmed'
    )
    
    if request.method == 'POST':
        registration.status = 'cancelled'
        registration.save()
        
        # Decrease current attendees count
        event.current_attendees -= 1
        event.save()
        
        messages.success(request, f'Registration for {event.title} has been cancelled.')
        return redirect('dashboard')
    
    return render(request, 'yosa/cancel_registration.html', {
        'event': event,
        'registration': registration,
    })

@login_required
def past_events(request):
    # Get past events the user registered for
    past_registrations = Registration.objects.filter(
        user=request.user,
        event__date__lt=timezone.now(),
        status='confirmed'
    ).select_related('event').order_by('-event__date')
    
    # Get all past events (not just user's)
    all_past_events = Event.objects.filter(
        date__lt=timezone.now(),
        is_active=True
    ).order_by('-date')
    
    context = {
        'past_registrations': past_registrations,
        'all_past_events': all_past_events,
    }
    return render(request, 'yosa/past_events.html', context)

@login_required
def events_list(request):
    events = Event.objects.filter(
        date__gte=timezone.now(),
        is_active=True
    ).order_by('date')
    return render(request, 'yosa/events.html', {'events': events})

@login_required
def messages_list(request):
    user_messages = Message.objects.filter(
        Q(receiver=request.user) | Q(is_feedback=True)
    ).order_by('-created_at')
    
    # Mark messages as read when viewed
    unread_messages = user_messages.filter(is_read=False)
    unread_messages.update(is_read=True)
    
    return render(request, 'yosa/messages.html', {
        'messages': user_messages,
    })

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('messages')
    else:
        form = MessageForm()
    
    return render(request, 'yosa/send_message.html', {'form': form})

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view this message
    if message.receiver != request.user and not message.is_feedback and message.sender != request.user:
        messages.error(request, 'You do not have permission to view this message.')
        return redirect('messages')
    
    # Mark as read
    if not message.is_read and message.receiver == request.user:
        message.is_read = True
        message.save()
    
    return render(request, 'yosa/message_detail.html', {
        'message': message,
    })

@login_required
@staff_member_required
def admin_dashboard(request):
    # Admin statistics
    total_users = User.objects.count()
    total_events = Event.objects.count()
    active_events = Event.objects.filter(is_active=True).count()
    total_registrations = Registration.objects.count()
    
    # Recent registrations
    recent_registrations = Registration.objects.select_related('user', 'event').order_by('-registration_date')[:10]
    
    # Upcoming events
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now(),
        is_active=True
    ).order_by('date')[:5]
    
    # Recent feedback
    recent_feedback = Message.objects.filter(
        is_feedback=True
    ).order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_events': total_events,
        'active_events': active_events,
        'total_registrations': total_registrations,
        'recent_registrations': recent_registrations,
        'upcoming_events': upcoming_events,
        'recent_feedback': recent_feedback,
    }
    return render(request, 'yosa/admin_dashboard.html', context)

@login_required
@staff_member_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Event created successfully!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventForm()
    
    return render(request, 'yosa/create_event.html', {'form': form})
@login_required
@staff_member_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'yosa/edit_event.html', {'form': form, 'event': event})
# Add error handler views
def custom_404_view(request, exception):
    return render(request, 'yosa/404.html', status=404)

def custom_500_view(request):
    return render(request, 'yosa/500.html', status=500)

def custom_403_view(request, exception):
    return render(request, 'yosa/403.html', status=403)

def custom_400_view(request, exception):
    return render(request, 'yosa/400.html', status=400)