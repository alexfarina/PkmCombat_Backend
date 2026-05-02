"""
URL configuration for PkmCombat_backend project.

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
from django.urls import path
from  rest_api import  views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register),
    path('login/', views.login),
    path('update_or_create_pokemon/<int:team_id>/<int:slot>/', views.update_or_create_pokemon),
    path('update_or_create_move/<int:team_id>/<int:slot>/', views.update_or_create_move),
    path('delete_team/<int:team_id>/', views.delete_team),
    path('delete_pkm_in_team/<int:team_id>/<int:slot_id>/', views.delete_pkm_in_team),
    path('get_all_teams/', views.get_all_teams),
    path('get_team/<int:team_id>/', views.get_team),
    path('accept_challenge/<int:battle_id>/', views.accept_challenge),
    path('create_battle/<int:user_team_id>/<int:opponent_team_id>/', views.create_battle),
    path('get_my_challenges/', views.get_my_challenges),
    path('choose_first_pkm/<int:slot>/<int:battle_id>/', views.choose_first_pkm),
]
