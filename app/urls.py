"""
URL configuration for app project.

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
from django.urls import path, include
from django.contrib import admin
from usuario.views import UserProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Obtendo token para o usuario
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Obtendo refresh token para o usuario
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Verificando se o token é valido
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Mostrando dados do usuario logado
    path('me/', UserProfileView.as_view(), name='user-profile'),
    #chamando a rota de urls de usuarios
    path('usuario/', include('usuario.urls')), 
    #chamando a rota de urls de clientes
    path('cliente/', include('cliente.urls')),
]
