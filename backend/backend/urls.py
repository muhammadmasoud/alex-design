from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt
from portfolio.views import (
    ProjectViewSet, ServiceViewSet, RegistrationView, LoginView, 
    CategorySubcategoriesView, AdminDashboardView, AdminCheckView, ContactView,
    ProjectImageViewSet, ServiceImageViewSet, ProjectAlbumView, ServiceAlbumView,
    CSRFTokenView, AdminStorageStatsView, AdminProjectViewSet, AdminServiceViewSet,
    OptimizationStatusView
)
from portfolio.category_views import (
    ProjectCategoryViewSet, ProjectSubcategoryViewSet,
    ServiceCategoryViewSet, ServiceSubcategoryViewSet, PublicCategoryView
)
from portfolio.consultation_views import (
    ConsultationSettingsViewSet, DayOffViewSet, BookingViewSet,
    PublicBookingView, AvailableTimeSlotsView, ConsultationSettingsPublicView,
    PublicDaysOffView, CheckMonthlyBookingView
)
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'project-images', ProjectImageViewSet, basename='projectimage')
router.register(r'service-images', ServiceImageViewSet, basename='serviceimage')
router.register(r'admin/projects', AdminProjectViewSet, basename='admin-projects')
router.register(r'admin/services', AdminServiceViewSet, basename='admin-services')
router.register(r'admin/project-categories', ProjectCategoryViewSet)
router.register(r'admin/project-subcategories', ProjectSubcategoryViewSet)
router.register(r'admin/service-categories', ServiceCategoryViewSet)
router.register(r'admin/service-subcategories', ServiceSubcategoryViewSet)

# Consultation booking system routes
router.register(r'admin/consultation-settings', ConsultationSettingsViewSet, basename='consultation-settings')
router.register(r'admin/days-off', DayOffViewSet, basename='days-off')
router.register(r'admin/bookings', BookingViewSet, basename='bookings')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/', csrf_exempt(RegistrationView.as_view()), name='register'),
    path('api/auth/login/', csrf_exempt(LoginView.as_view()), name='login'),
    path('api/categories/subcategories/', CategorySubcategoriesView.as_view(), name='category-subcategories'),
    path('api/categories/public/', PublicCategoryView.as_view(), name='public-categories'),
    path('api/admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('api/admin/storage-stats/', AdminStorageStatsView.as_view(), name='admin-storage-stats'),
    path('api/admin/check/', csrf_exempt(AdminCheckView.as_view()), name='admin-check'),
    path('api/admin/optimization-status/', OptimizationStatusView.as_view(), name='optimization-status'),
    path('api/csrf-token/', CSRFTokenView.as_view(), name='csrf-token'),
    path('api/contact/', csrf_exempt(ContactView.as_view()), name='contact'),
    path('api/projects/<int:project_id>/album/', ProjectAlbumView.as_view(), name='project-album'),
    path('api/services/<int:service_id>/album/', ServiceAlbumView.as_view(), name='service-album'),
    
    # Consultation booking system endpoints
    path('api/consultations/book/', csrf_exempt(PublicBookingView.as_view()), name='public-booking'),
    path('api/consultations/available-slots/', AvailableTimeSlotsView.as_view(), name='available-slots'),
    path('api/consultations/settings/', ConsultationSettingsPublicView.as_view(), name='consultation-settings-public'),
    path('api/consultations/days-off/', PublicDaysOffView.as_view(), name='public-days-off'),
    path('api/consultations/check-monthly/', CheckMonthlyBookingView.as_view(), name='check-monthly-booking'),
]

# Enhanced media file serving for better image loading
if settings.DEBUG:
    # Development: serve media files directly
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production: serve media files with proper headers
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': False,
        }),
    ]


