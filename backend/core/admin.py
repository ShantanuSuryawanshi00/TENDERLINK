from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Tender, Bid

# 1. Register User Model
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'company_name', 'is_verified')
    list_filter = ('role', 'is_verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Account Role', {'fields': ('role', 'company_name', 'phone', 'is_verified')}),
    )

# 2. Register Tender Model
@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'budget', 'deadline', 'status', 'posted_by')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'created_at'

# 3. Register Bid Model
@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('tender', 'bidder', 'bid_amount', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
