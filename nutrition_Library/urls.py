from django.contrib import admin
from django.urls import path, include
from nutrition import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('nutrition.urls')),  # Aquí se incluye todo lo que está en nutrition/urls.py
    path('accounts/', include('django.contrib.auth.urls')),  # Rutas de Django Auth para login, logout, password change, etc.
    path('password_reset/', views.request_password_reset, name='password_reset'),
    path('password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_complete/', views.password_reset_complete, name='password_reset_complete'),
]

