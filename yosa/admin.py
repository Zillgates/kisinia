from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Event, Registration, Message, Trending

# Custom User Display
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'bio', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

# Inline for Registrations in Event Admin
class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ('registration_date',)
    can_delete = True

# Event Admin
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'date', 'location', 'max_attendees', 'current_attendees', 'is_active')
    list_filter = ('event_type', 'is_active')
    search_fields = ('title', 'description', 'location')
    inlines = [RegistrationInline]
    readonly_fields = ('current_attendees',)

# Registration Admin
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registration_date', 'status')
    list_filter = ('status', 'registration_date')
    search_fields = ('user__username', 'event__title')

# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'receiver', 'is_feedback', 'is_read', 'created_at')
    list_filter = ('is_feedback', 'is_read', 'created_at')
    search_fields = ('subject', 'content', 'sender__username')

# Trending Admin
@admin.register(Trending)
class TrendingAdmin(admin.ModelAdmin):
    list_display = ('event', 'views', 'clicks', 'last_updated')
    list_filter = ('last_updated',)

# Register User model
admin.site.register(User, UserAdmin)

# Custom admin site headers
admin.site.site_header = "Kisinia Yosa Administration"
admin.site.site_title = "Kisinia Yosa Admin"
admin.site.index_title = "Welcome to Kisinia Yosa Admin Portal"
