from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.list_create, name='list'),
    path('reset/', views.reset_view, name='reset'),
    path('delete/<int:pk>/', views.delete_tx, name='delete'),
]
