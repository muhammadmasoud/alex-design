from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt
from portfolio.views import (
    ProjectViewSet, ServiceViewSet, RegistrationView, LoginView, 
    CategorySubcategoriesView, AdminDashboardView, AdminCheckView, ContactView,
    ProjectImageViewSet, ServiceImageViewSet, ProjectAlbumView, ServiceAlbumView,
    CSRFTokenView, AdminStorageStatsView
)
from portfolio.category_views import (
    ProjectCategoryViewSet, ProjectSubcategoryViewSet,
    ServiceCategoryViewSet, ServiceSubcategoryViewSet
)
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'project-images', ProjectImageViewSet, basename='projectimage')
router.register(r'service-images', ServiceImageViewSet, basename='serviceimage')
router.register(r'admin/project-categories', ProjectCategoryViewSet)
router.register(r'admin/project-subcategories', ProjectSubcategoryViewSet)
router.register(r'admin/service-categories', ServiceCategoryViewSet)
router.register(r'admin/service-subcategories', ServiceSubcategoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/', csrf_exempt(RegistrationView.as_view()), name='register'),
    path('api/auth/login/', csrf_exempt(LoginView.as_view()), name='login'),
    path('api/categories/subcategories/', CategorySubcategoriesView.as_view(), name='category-subcategories'),
    path('api/admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('api/admin/storage-stats/', AdminStorageStatsView.as_view(), name='admin-storage-stats'),
    path('api/admin/check/', csrf_exempt(AdminCheckView.as_view()), name='admin-check'),
    path('api/csrf-token/', CSRFTokenView.as_view(), name='csrf-token'),
    path('api/contact/', csrf_exempt(ContactView.as_view()), name='contact'),
    path('api/projects/<int:project_id>/album/', ProjectAlbumView.as_view(), name='project-album'),
    path('api/services/<int:service_id>/album/', ServiceAlbumView.as_view(), name='service-album'),
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
