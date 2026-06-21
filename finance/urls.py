from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.list_create, name='list'),
    path('delete/<int:pk>/', views.delete_tx, name='delete'),
]
