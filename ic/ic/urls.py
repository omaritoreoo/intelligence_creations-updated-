"""
URL configuration for ic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

# Impor semua ViewSet Anda dari projek.viewset_api
from projek.viewset_api import (
    ProjectViewSet, IntelligenceEngineeringViewSet, ProblemFramingViewSet,
    DatasetRequestViewSet, DataProcessingViewSet, TrainingModelViewSet
)
router = routers.DefaultRouter()
router.register('projects', ProjectViewSet) # Endpoint: /api-content/projects/
router.register('intelligence-engineerings', IntelligenceEngineeringViewSet) # Endpoint: /api-content/intelligence-engineerings/
router.register('problem-framings', ProblemFramingViewSet) # Endpoint: /api-content/problem-framings/
router.register('dataset-requests', DatasetRequestViewSet) # Endpoint: /api-content/dataset-requests/
router.register('data-processings', DataProcessingViewSet) # Endpoint: /api-content/data-processings/
router.register('training-models', TrainingModelViewSet) # Endpoint: /api-content/training-models/

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('projek.urls', 'projek'), namespace='projek')),
    path('api-content/', include(router.urls)),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

