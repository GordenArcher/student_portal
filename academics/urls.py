
from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<uuid:subject_id>/update/', views.subject_update, name='subject_update'),
    path('subjects/<uuid:subject_id>/delete/', views.subject_delete, name='subject_delete'),
    
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create, name='class_create'),
    path('classes/<uuid:class_id>/update/', views.class_update, name='class_update'),
    path('classes/<uuid:class_id>/delete/', views.class_delete, name='class_delete'),
]