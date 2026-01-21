from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка Swagger документации
schema_view = get_schema_view(
    openapi.Info(
        title="Chat API",
        default_version='v1',
        description="API для управления чатами и сообщениями",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@chatapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Админ панель
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('chat_app.urls')),
    
    # Swagger документация
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]