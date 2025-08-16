from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    Project, Service, User, 
    ProjectCategory, ProjectSubcategory, 
    ServiceCategory, ServiceSubcategory,
    ProjectImage, ServiceImage
)

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3  # Allow multiple empty forms for bulk upload
    fields = ('image', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    ordering = ['order', 'created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    class Media:
        js = ('admin/js/bulk_upload.js',)  # Custom JS for bulk upload (optional)
        css = {
            'all': ('admin/css/bulk_upload.css',)  # Custom CSS for better styling
        }

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 3  # Allow multiple empty forms for bulk upload
    fields = ('image', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    ordering = ['order', 'created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    class Media:
        js = ('admin/js/bulk_upload.js',)  # Custom JS for bulk upload (optional)
        css = {
            'all': ('admin/css/bulk_upload.css',)  # Custom CSS for better styling
        }

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'subcategory', 'image_preview', 'album_count', 'created_at')
    list_filter = ('category', 'subcategory', 'created_at')
    search_fields = ('title', 'description', 'category__name', 'subcategory__name')
    readonly_fields = ('image_preview', 'album_count', 'created_at')
    ordering = ('-created_at',)
    inlines = [ProjectImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Categorization', {
            'fields': ('category', 'subcategory'),
            'description': 'Choose a category first, then select an appropriate subcategory.'
        }),
        ('Main Display Image', {
            'fields': ('image', 'image_preview'),
            'description': 'This image will be shown as the main project image in listings and details.'
        }),
        ('Project Album', {
            'fields': ('album_count',),
            'description': 'Add multiple images to the project album using the "Album Images" section below. Visitors can view all images by clicking "View Album" on the project detail page.',
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Image Preview"
    
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter subcategories based on selected category"""
        if db_field.name == "subcategory":
            kwargs["queryset"] = ProjectSubcategory.objects.select_related('category').order_by('category__name', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'subcategory', 'icon_preview', 'album_count')
    list_filter = ('category', 'subcategory')
    search_fields = ('name', 'description', 'category__name', 'subcategory__name')
    readonly_fields = ('icon_preview', 'album_count')
    inlines = [ServiceImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price')
        }),
        ('Categorization', {
            'fields': ('category', 'subcategory'),
            'description': 'Choose a category first, then select an appropriate subcategory.'
        }),
        ('Main Display Icon', {
            'fields': ('icon', 'icon_preview'),
            'description': 'This icon will be shown as the main service icon in listings and details.'
        }),
        ('Service Album', {
            'fields': ('album_count',),
            'description': 'Add multiple images to the service album using the "Album Images" section below. Visitors can view all images by clicking "View Album" on the service detail page.',
            'classes': ('collapse',)
        }),
    )
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.icon.url
            )
        return "No icon"
    icon_preview.short_description = "Icon Preview"
    
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
    list_display = ('project', 'title', 'order', 'image_preview', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('project__title', 'title', 'description')
    readonly_fields = ('image_preview', 'created_at')
    ordering = ('project', 'order', 'created_at')
    
    fieldsets = (
        ('Project Information', {
            'fields': ('project',)
        }),
        ('Image Details', {
            'fields': ('image', 'image_preview', 'title', 'description', 'order')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Image Preview"


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ('service', 'title', 'order', 'image_preview', 'created_at')
    list_filter = ('service', 'created_at')
    search_fields = ('service__name', 'title', 'description')
    readonly_fields = ('image_preview', 'created_at')
    ordering = ('service', 'order', 'created_at')
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service',)
        }),
        ('Image Details', {
            'fields': ('image', 'image_preview', 'title', 'description', 'order')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Image Preview"
