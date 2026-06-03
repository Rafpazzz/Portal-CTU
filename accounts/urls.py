from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('password_reset_form/', views.password_reset_form, name='password_reset_form'),
    path('perfil/', views.perfil, name='perfil'),
]
