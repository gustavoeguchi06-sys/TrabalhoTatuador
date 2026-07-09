from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.list_create, name='list'),
    path('delete/<int:pk>/', views.delete_tx, name='delete'),
    path('agenda/', views.agenda, name='agenda'),
    path('agenda/<int:pk>/status/', views.appointment_status, name='appointment_status'),
    path('agenda/<int:pk>/excluir/', views.appointment_delete, name='appointment_delete'),
    path('push/vapid/', views.vapid_public_key, name='vapid_public_key'),
    path('push/subscribe/', views.push_subscribe, name='push_subscribe'),
    path('push/test/', views.push_test, name='push_test'),
]
