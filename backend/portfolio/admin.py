from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    Project, Service, User, 
    ProjectCategory, ProjectSubcategory, 
    ServiceCategory, ServiceSubcategory,
    ProjectImage, ServiceImage,
    ConsultationSettings, DayOff, Booking
)

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3  # Allow multiple empty forms for bulk upload
    fields = ('image', 'order', 'image_preview', 'optimized_paths')
    readonly_fields = ('image_preview', 'optimized_paths')
    ordering = ['order']
    
    def image_preview(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<img src="/media/{}" style="max-height: 60px; max-width: 60px;" />',
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def optimized_paths(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<strong>Currently:</strong> <span style="color: green;">{}</span><br>'
                '<strong>Optimized:</strong> <span style="color: blue;">{}</span>',
                obj.image.name if obj.image else "No image",
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<strong>Currently:</strong> <span style="color: orange;">{}</span><br>'
                '<strong>Status:</strong> <span style="color: red;">Not optimized</span>',
                obj.image.name
            )
        return "No image"
    optimized_paths.short_description = "Image Paths"
    
    class Media:
        js = ('admin/js/bulk_upload.js',)  # Custom JS for bulk upload (optional)
        css = {
            'all': ('admin/css/bulk_upload.css',)  # Custom CSS for better styling
        }

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 3  # Allow multiple empty forms for bulk upload
    fields = ('image', 'order', 'image_preview', 'optimized_paths')
    readonly_fields = ('image_preview', 'optimized_paths')
    ordering = ['order']
    
    def image_preview(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<img src="/media/{}" style="max-height: 60px; max-width: 60px;" />',
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def optimized_paths(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<strong>Currently:</strong> <span style="color: green;">{}</span><br>'
                '<strong>Optimized:</strong> <span style="color: blue;">{}</span>',
                obj.image.name if obj.image else "No image",
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<strong>Currently:</strong> <span style="color: orange;">{}</span><br>'
                '<strong>Status:</strong> <span style="color: red;">Not optimized</span>',
                obj.image.name
            )
        return "No image"
    optimized_paths.short_description = "Image Paths"
    
    class Media:
        js = ('admin/js/bulk_upload.js',)  # Custom JS for bulk upload (optional)
        css = {
            'all': ('admin/css/bulk_upload.css',)  # Custom CSS for better styling
        }

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_categories', 'display_subcategories', 'project_date', 'order', 'image_preview', 'album_count')
    list_filter = ('categories', 'subcategories', 'project_date')
    search_fields = ('title', 'description', 'categories__name', 'subcategories__name')
    readonly_fields = ('image_preview', 'album_count', 'optimized_paths')
    ordering = ('order', '-project_date')
    list_editable = ('order',)
    inlines = [ProjectImageInline]
    filter_horizontal = ('categories', 'subcategories')  # Add this for better many-to-many interface
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'project_date')
        }),
        ('Display Order', {
            'fields': ('order',),
            'description': 'Projects are ordered by this field first, then by project date (newest first). Lower numbers appear first.'
        }),
        ('Categorization', {
            'fields': ('categories', 'subcategories'),
            'description': 'Choose one or more categories and subcategories for this project.'
        }),
        ('Main Display Image', {
            'fields': ('image', 'image_preview', 'optimized_paths'),
            'description': 'This image will be shown as the main project image in listings and details.'
        }),
        ('Project Album', {
            'fields': ('album_count',),
            'description': 'Add multiple images to the project album using the "Album Images" section below. Visitors can view all images by clicking "View Album" on the project detail page.',
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to add error handling"""
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving project {obj.title}: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise e
    
    def save_formset(self, request, form, formset, change):
        """Override save_formset to add error handling"""
        try:
            super().save_formset(request, form, formset, change)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving project formset: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise e
    
    def image_preview(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<img src="/media/{}" style="max-height: 100px; max-width: 100px;" />',
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Image Preview"
    
    def optimized_paths(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<strong>Currently:</strong> <span style="color: green;">{}</span><br>'
                '<strong>Optimized:</strong> <span style="color: blue;">{}</span>',
                obj.image.name if obj.image else "No image",
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<strong>Currently:</strong> <span style="color: orange;">{}</span><br>'
                '<strong>Status:</strong> <span style="color: red;">Not optimized</span>',
                obj.image.name
            )
        return "No image"
    optimized_paths.short_description = "Image Paths"
    
    def album_count(self, obj):
        """Show the number of album images"""
        count = obj.album_images.count()
        if count == 0:
            return "No album images"
        elif count == 1:
            return "1 album image"
        else:
            return f"{count} album images"
    album_count.short_description = "Album Images"
    
    def display_categories(self, obj):
        """Display all categories for this project"""
        categories = obj.categories.all()
        if categories:
            return ", ".join([cat.name for cat in categories])
        return "No categories"
    display_categories.short_description = "Categories"
    
    def display_subcategories(self, obj):
        """Display all subcategories for this project"""
        subcategories = obj.subcategories.all()
        if subcategories:
            return ", ".join([subcat.name for subcat in subcategories])
        return "No subcategories"
    display_subcategories.short_description = "Subcategories"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter subcategories based on selected category"""
        if db_field.name == "subcategory":
            kwargs["queryset"] = ProjectSubcategory.objects.select_related('category').order_by('category__name', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'display_categories', 'display_subcategories', 'order', 'icon_preview', 'album_count')
    list_filter = ('categories', 'subcategories')
    search_fields = ('name', 'description', 'categories__name', 'subcategories__name')
    readonly_fields = ('icon_preview', 'album_count', 'optimized_paths')
    ordering = ('order', 'name')
    list_editable = ('order',)
    inlines = [ServiceImageInline]
    filter_horizontal = ('categories', 'subcategories')  # Add this for better many-to-many interface
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price')
        }),
        ('Display Order', {
            'fields': ('order',),
            'description': 'Services are ordered by this field first, then by name. Lower numbers appear first.'
        }),
        ('Categorization', {
            'fields': ('categories', 'subcategories'),
            'description': 'Choose one or more categories and subcategories for this service.'
        }),
        ('Main Display Icon', {
            'fields': ('icon', 'icon_preview', 'optimized_paths'),
            'description': 'This icon will be shown as the main service icon in listings and details.'
        }),
        ('Service Album', {
            'fields': ('album_count',),
            'description': 'Add multiple images to the service album using the "Album Images" section below. Visitors can view all images by clicking "View Album" on the service detail page.',
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to add error handling"""
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving service {obj.name}: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise e
    
    def save_formset(self, request, form, formset, change):
        """Override save_formset to add error handling"""
        try:
            super().save_formset(request, form, formset, change)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving service formset: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise e
    
    def icon_preview(self, obj):
        if obj.optimized_icon_medium:
            return format_html(
                '<img src="/media/{}" style="max-height: 100px; max-width: 100px;" />',
                obj.optimized_icon_medium
            )
        elif obj.icon:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.icon.url
            )
        return "No icon"
    icon_preview.short_description = "Icon Preview"
    
    def optimized_paths(self, obj):
        if obj.optimized_icon_medium:
            return format_html(
                '<strong>Currently:</strong> <span style="color: green;">{}</span><br>'
                '<strong>Optimized:</strong> <span style="color: blue;">{}</span>',
                obj.icon.name if obj.icon else "No icon",
                obj.optimized_icon_medium
            )
        elif obj.icon:
            return format_html(
                '<strong>Currently:</strong> <span style="color: orange;">{}</span><br>'
                '<strong>Status:</strong> <span style="color: red;">Not optimized</span>',
                obj.icon.name
            )
        return "No icon"
    optimized_paths.short_description = "Icon Paths"
    
    def album_count(self, obj):
        """Show the number of album images"""
        count = obj.album_images.count()
        if count == 0:
            return "No album images"
        elif count == 1:
            return "1 album image"
        else:
            return f"{count} album images"
    album_count.short_description = "Album Images"
    
    def display_categories(self, obj):
        """Display all categories for this service"""
        categories = obj.categories.all()
        if categories:
            return ", ".join([cat.name for cat in categories])
        return "No categories"
    display_categories.short_description = "Categories"
    
    def display_subcategories(self, obj):
        """Display all subcategories for this service"""
        subcategories = obj.subcategories.all()
        if subcategories:
            return ", ".join([subcat.name for subcat in subcategories])
        return "No subcategories"
    display_subcategories.short_description = "Subcategories"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter subcategories based on selected category"""
        if db_field.name == "subcategory":
            kwargs["queryset"] = ServiceSubcategory.objects.select_related('category').order_by('category__name', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    actions = ['delete_selected', 'activate_users', 'deactivate_users']
    
    def activate_users(self, request, queryset):
        """Custom action to activate selected users"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} users were activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Custom action to deactivate selected users"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} users were deactivated.')
    deactivate_users.short_description = "Deactivate selected users"


# Dynamic Category Models Admin
@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'subcategories_count', 'projects_count', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'subcategories_count', 'projects_count')
    ordering = ('name',)
    
    def subcategories_count(self, obj):
        return obj.subcategories.count()
    subcategories_count.short_description = "Subcategories"
    
    def projects_count(self, obj):
        """Count projects in this category and its subcategories"""
        direct_projects = obj.projects.count()
        subcategory_projects = sum(
            subcat.projects.count() 
            for subcat in obj.subcategories.all()
        )
        return direct_projects + subcategory_projects
    projects_count.short_description = "Total Projects"
    
    def delete_model(self, request, obj):
        """Custom delete with validation"""
        total_projects = self.projects_count(obj)
        if total_projects > 0:
            from django.contrib import messages
            messages.error(
                request, 
                f'Cannot delete category "{obj.name}". It has {total_projects} project(s) associated with it or its subcategories.'
            )
            return
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Custom bulk delete with validation"""
        from django.contrib import messages
        errors = []
        for obj in queryset:
            total_projects = self.projects_count(obj)
            if total_projects > 0:
                errors.append(f'"{obj.name}" has {total_projects} project(s)')
        
        if errors:
            messages.error(
                request, 
                f'Cannot delete some categories: {", ".join(errors)}'
            )
            return
        
        super().delete_queryset(request, queryset)


@admin.register(ProjectSubcategory)
class ProjectSubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'projects_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('created_at', 'projects_count')
    ordering = ('category__name', 'name')
    
    def projects_count(self, obj):
        return obj.projects.count()
    projects_count.short_description = "Projects"


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'subcategories_count', 'services_count', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'subcategories_count', 'services_count')
    ordering = ('name',)
    
    def subcategories_count(self, obj):
        return obj.subcategories.count()
    subcategories_count.short_description = "Subcategories"
    
    def services_count(self, obj):
        """Count services in this category and its subcategories"""
        direct_services = obj.services.count()
        subcategory_services = sum(
            subcat.services.count() 
            for subcat in obj.subcategories.all()
        )
        return direct_services + subcategory_services
    services_count.short_description = "Total Services"
    
    def delete_model(self, request, obj):
        """Custom delete with validation"""
        total_services = self.services_count(obj)
        if total_services > 0:
            from django.contrib import messages
            messages.error(
                request, 
                f'Cannot delete category "{obj.name}". It has {total_services} service(s) associated with it or its subcategories.'
            )
            return
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Custom bulk delete with validation"""
        from django.contrib import messages
        errors = []
        for obj in queryset:
            total_services = self.services_count(obj)
            if total_services > 0:
                errors.append(f'"{obj.name}" has {total_services} service(s)')
        
        if errors:
            messages.error(
                request, 
                f'Cannot delete some categories: {", ".join(errors)}'
            )
            return
        
        super().delete_queryset(request, queryset)


@admin.register(ServiceSubcategory)
class ServiceSubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'services_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('created_at', 'services_count')
    ordering = ('category__name', 'name')
    
    def services_count(self, obj):
        return obj.services.count()
    services_count.short_description = "Services"


# Register Album Image Models individually for advanced management
@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'order', 'image_preview')
    list_filter = ('project',)
    search_fields = ('project__title', 'title', 'description')
    readonly_fields = ('image_preview', 'optimized_paths')
    ordering = ('project', 'order')
    
    fieldsets = (
        ('Project Information', {
            'fields': ('project',)
        }),
        ('Image Details', {
            'fields': ('image', 'image_preview', 'title', 'description', 'order', 'optimized_paths')
        }),
    )
    
    def image_preview(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<img src="/media/{}" style="max-height: 100px; max-width: 100px;" />',
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Image Preview"
    
    def optimized_paths(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<strong>Currently:</strong> <span style="color: green;">{}</span><br>'
                '<strong>Optimized:</strong> <span style="color: blue;">{}</span>',
                obj.image.name if obj.image else "No image",
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<strong>Currently:</strong> <span style="color: orange;">{}</span><br>'
                '<strong>Status:</strong> <span style="color: red;">Not optimized</span>',
                obj.image.name
            )
        return "No image"
    optimized_paths.short_description = "Image Paths"


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ('service', 'title', 'order', 'image_preview')
    list_filter = ('service',)
    search_fields = ('service__name', 'title', 'description')
    readonly_fields = ('image_preview', 'optimized_paths')
    ordering = ('service', 'order')
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service',)
        }),
        ('Image Details', {
            'fields': ('image', 'image_preview', 'title', 'description', 'order', 'optimized_paths')
        }),
    )
    
    def image_preview(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<img src="/media/{}" style="max-height: 100px; max-width: 100px;" />',
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Image Preview"
    
    def optimized_paths(self, obj):
        if obj.optimized_image_medium:
            return format_html(
                '<strong>Currently:</strong> <span style="color: green;">{}</span><br>'
                '<strong>Optimized:</strong> <span style="color: blue;">{}</span>',
                obj.image.name if obj.image else "No image",
                obj.optimized_image_medium
            )
        elif obj.image:
            return format_html(
                '<strong>Currently:</strong> <span style="color: orange;">{}</span><br>'
                '<strong>Status:</strong> <span style="color: red;">Not optimized</span>',
                obj.image.name
            )
        return "No image"
    optimized_paths.short_description = "Image Paths"


# Consultation Booking System Admin
@admin.register(ConsultationSettings)
class ConsultationSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'booking_enabled', 'meeting_duration_minutes', 'buffer_time_minutes', 'advance_booking_days', 'minimum_notice_hours', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Meeting Configuration', {
            'fields': ('booking_enabled', 'meeting_duration_minutes', 'buffer_time_minutes'),
            'description': 'Basic settings for consultation meetings.'
        }),
        ('Working Hours', {
            'fields': (
                'monday_hours', 'tuesday_hours', 'wednesday_hours', 
                'thursday_hours', 'friday_hours', 'saturday_hours', 'sunday_hours'
            ),
            'description': 'Set working hours for each day (e.g., "09:00-17:00") or leave empty for days off.'
        }),
        ('Booking Rules', {
            'fields': ('advance_booking_days', 'minimum_notice_hours'),
            'description': 'Rules for when clients can book consultations.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Only allow one settings instance"""
        return not ConsultationSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings"""
        return False


@admin.register(DayOff)
class DayOffAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('reason',)
    readonly_fields = ('created_at',)
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Day Off Information', {
            'fields': ('date', 'reason')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Show future and recent days off"""
        from datetime import date, timedelta
        # Show days off from 30 days ago onwards
        cutoff_date = date.today() - timedelta(days=30)
        return super().get_queryset(request).filter(date__gte=cutoff_date)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_email', 'date', 'time', 'duration_minutes', 'status', 'created_at', 'is_past_due')
    list_filter = ('status', 'date', 'created_at', 'duration_minutes')
    search_fields = ('client_name', 'client_email', 'project_details', 'message')
    readonly_fields = ('created_at', 'updated_at', 'is_past_due', 'get_end_time', 'get_datetime_range')
    ordering = ('-date', '-time')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_name', 'client_email', 'client_phone')
        }),
        ('Booking Details', {
            'fields': ('date', 'time', 'duration_minutes', 'get_end_time', 'status')
        }),
        ('Project Information', {
            'fields': ('project_details', 'message'),
            'classes': ('collapse',)
        }),
        ('Admin Management', {
            'fields': ('admin_notes', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_past_due', 'get_datetime_range'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_confirmed', 'mark_cancelled', 'mark_completed', 'mark_no_show']
    
    def is_past_due(self, obj):
        """Show if the booking is in the past"""
        past = obj.is_past()
        if past:
            return format_html('<span style="color: red;">✗ Past</span>')
        return format_html('<span style="color: green;">✓ Future</span>')
    is_past_due.short_description = "Status"
    is_past_due.admin_order_field = 'date'
    
    def get_end_time(self, obj):
        """Show the end time of the consultation"""
        return obj.get_end_time()
    get_end_time.short_description = "End Time"
    
    def get_datetime_range(self, obj):
        """Show the full datetime range"""
        start_dt, end_dt = obj.get_datetime_range()
        return format_html(
            '<strong>Start:</strong> {}<br><strong>End:</strong> {}',
            start_dt.strftime('%Y-%m-%d %H:%M'),
            end_dt.strftime('%Y-%m-%d %H:%M')
        )
    get_datetime_range.short_description = "Full Schedule"
    
    # Custom actions
    def mark_confirmed(self, request, queryset):
        """Mark selected bookings as confirmed"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} booking(s) marked as confirmed.')
    mark_confirmed.short_description = "Mark selected bookings as confirmed"
    
    def mark_cancelled(self, request, queryset):
        """Mark selected bookings as cancelled"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} booking(s) marked as cancelled.')
    mark_cancelled.short_description = "Mark selected bookings as cancelled"
    
    def mark_completed(self, request, queryset):
        """Mark selected bookings as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} booking(s) marked as completed.')
    mark_completed.short_description = "Mark selected bookings as completed"
    
    def mark_no_show(self, request, queryset):
        """Mark selected bookings as no show"""
        updated = queryset.update(status='no_show')
        self.message_user(request, f'{updated} booking(s) marked as no show.')
    mark_no_show.short_description = "Mark selected bookings as no show"
    
    def get_queryset(self, request):
        """Optimize queries and show recent bookings"""
        from datetime import date, timedelta
        # Show bookings from 90 days ago onwards to keep admin manageable
        cutoff_date = date.today() - timedelta(days=90)
        return super().get_queryset(request).filter(date__gte=cutoff_date)
