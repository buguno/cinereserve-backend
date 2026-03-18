"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.http import JsonResponse
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


def api_root(request):
    return JsonResponse({
        'message': 'Welcome to CineReserve API',
        'docs': ['/docs/', '/redoc/'],
    })


schema_view = get_schema_view(
    openapi.Info(
        title='CineReserve API',
        default_version='v1',
        description='CineReserve API Documentation',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', api_root),
    path(
        'docs/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc',
    ),
    path('admin/', admin.site.urls),
    path('api/movies/', include('movies.urls')),
    path('api/showtimes/', include('showtimes.urls')),
    path('api/tickets/', include('tickets.urls')),
    path('api/users/', include('users.urls')),
]
