"""
URL configuration for lecture_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from rest_framework import routers

from .views import APIRootView
from authentication import views as auth_views
from courses import views as course_views
from notifications import views as notification_views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"auth", auth_views.AuthViewSet, basename="auth")
router.register(r"users", auth_views.UserViewSet, basename="users")
router.register(r"courses", course_views.CourseViewSet, basename="courses")
router.register(
    r"notifications", notification_views.NotificationViewSet, basename="notifications"
)

urlpatterns = [
    path("", APIRootView.as_view(), name="api-root"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    # YOUR PATTERNS
    path("api/docs", SpectacularAPIView.as_view(), name="docs"),
    # Optional UI:
    path(
        "api/docs/swagger-ui",
        SpectacularSwaggerView.as_view(url_name="docs"),
        name="swagger-ui",
    ),
    path("api/docs/redoc", SpectacularRedocView.as_view(url_name="docs"), name="redoc"),
]
