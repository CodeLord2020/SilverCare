from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter
from import_export import resources
from .models import User

class UserResource(resources.ModelResource):
    """
    Resource class for importing/exporting user data
    """
    class Meta:
        model = User
        fields = (
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'user_type', 
            'is_verified', 
            'created_at'
        )
        export_order = fields
        import_id_fields = ('email',)


class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    resource_classes = UserResource
    
    list_display = (
        'email', 
        'get_full_name', 
        'user_type', 
        'is_verified', 
        'is_active', 
        'created_at'
    )

    # Filtering options
    list_filter = (
        ('user_type', admin.ChoicesFieldListFilter),
        'is_verified', 
        'is_active',
        ('created_at', DateRangeFilter)
    )

    # Search fields
    search_fields = (
        'email', 
        'first_name', 
        'last_name', 
        'phone_number'
    )

    # Fieldsets for detailed view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 
                'last_name', 
                'profile_picture',
                'phone_number', 
                'backup_phone_number'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'user_type',
                'is_verified',
                'is_active', 
                'is_staff', 
                'is_superuser'
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login', 
                'created_at', 
                'updated_at'
            )
        }),
    )

    # Customize add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'first_name', 
                'last_name', 
                'phone_number', 
                'user_type',
                'password1', 
                'password2'
            )
        }),
    )

    # Ordering
    ordering = ('-created_at',)

    # Custom methods
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'