from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import User, Event, Registration, Message

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'bio', 'avatar')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional if needed
        self.fields['avatar'].required = False

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_type', 'date', 'location', 'max_attendees', 'image']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now():
            raise forms.ValidationError("Event date cannot be in the past.")
        return date
    
    def clean_max_attendees(self):
        max_attendees = self.cleaned_data.get('max_attendees')
        if max_attendees and max_attendees <= 0:
            raise forms.ValidationError("Maximum attendees must be greater than 0.")
        return max_attendees

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ('special_requests',)
        widgets = {
            'special_requests': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Any special requests or dietary restrictions?'
            }),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('subject', 'content', 'receiver')
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Subject'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your message...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make receiver optional for feedback messages
        self.fields['receiver'].required = False
        # Filter users for receiver field (exclude current user)
        if 'request' in kwargs:
            request = kwargs.pop('request')
            self.fields['receiver'].queryset = User.objects.exclude(id=request.user.id)

class FeedbackForm(forms.ModelForm):
    # Add dropdown choices for subject
    SUBJECT_CHOICES = [
        ('', 'Select a subject...'),
        ('general', 'General Feedback'),
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('event', 'Event Feedback'),
        ('registration', 'Registration Issue'),
        ('payment', 'Payment Issue'),
        ('other', 'Other'),
    ]
    
    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'required'
        }),
        label="Subject"
    )
    
    # Add email and phone fields
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        }),
        label="Email Address"
    )
    
    phone = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number (optional)'
        }),
        label="Phone Number"
    )
    
    # Customize the content field
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8,
            'class': 'form-control',
            'placeholder': 'Please describe your feedback in detail...'
        }),
        label="Your Message"
    )
    
    class Meta:
        model = Message
        fields = ('subject', 'content')
    
    def __init__(self, *args, **kwargs):
        # Get the user instance if passed
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill email if user is logged in
        if self.user and self.user.is_authenticated:
            self.fields['email'].initial = self.user.email
            self.fields['phone'].initial = self.user.phone
    
    def save(self, commit=True):
        message = super().save(commit=False)
        message.is_feedback = True
        message.sender = self.user if self.user and self.user.is_authenticated else None
        
        # Store email and phone in content (or create a custom field)
        email = self.cleaned_data.get('email', '')
        phone = self.cleaned_data.get('phone', '')
        
        # Add contact info to the message
        contact_info = f"\n\n---\nContact Information:\nEmail: {email}"
        if phone:
            contact_info += f"\nPhone: {phone}"
        
        message.content = self.cleaned_data['content'] + contact_info
        
        if commit:
            message.save()
        return message