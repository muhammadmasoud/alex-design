from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt
from portfolio.views import (
    ProjectViewSet, ServiceViewSet, RegistrationView, LoginView, 
    CategorySubcategoriesView, AdminDashboardView, AdminCheckView, ContactView
)
from portfolio.category_views import (
    ProjectCategoryViewSet, ProjectSubcategoryViewSet,
    ServiceCategoryViewSet, ServiceSubcategoryViewSet
)
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'services', ServiceViewSet)
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
    path('api/admin/check/', csrf_exempt(AdminCheckView.as_view()), name='admin-check'),
    path('api/contact/', ContactView.as_view(), name='contact'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
