
from django.urls import path
from . import views


urlpatterns = [
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<uuid:subject_id>/update/', views.subject_update, name='subject_update'),
    path('subjects/<uuid:subject_id>/delete/', views.subject_delete, name='subject_delete'),
    path('subjects/<uuid:subject_id>/data/', views.get_subject_data, name='get_subject_data'),
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create, name='class_create'),
    path('classes/<str:class_id>/update/', views.class_update, name='class_update'),
    path('classes/<str:class_id>/delete/', views.class_delete, name='class_delete'),
    path('classes/<str:class_id>/data/', views.get_class_data, name='get_class_data'),
    path('api/teachers/', views.get_teachers_list, name='get_teachers_list'),
    path('api/subjects/', views.get_subjects_list, name='get_subjects_list'),
    path('classes/<str:class_id>/assign-teacher/', views.assign_teacher_to_class, name='assign_teacher_to_class'),
    path('classes/<str:class_id>/assign-subjects/', views.assign_subjects_to_class, name='assign_subjects_to_class'),
]