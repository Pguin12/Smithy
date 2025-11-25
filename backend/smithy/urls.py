from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.get_all_items, name='get_all_items'),
    path('recipes/', views.get_all_recipes, name='get_all_recipes'),
    path('combine/', views.combine_items, name='combine_items'),
    path('user/', views.get_user, name='get_user'),
]
