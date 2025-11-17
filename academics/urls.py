
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
    path('academic-years/', views.get_academic_years, name='get_academic_years'),
    path('academic-list/', views.academic_years_list, name='academic_years_list'),
    path('academic-years/create/', views.create_academic_year, name='create_academic_year'),
    path('subjects/<uuid:subject_id>/assign-teacher/', views.assign_teacher_to_subject, name='assign_teacher_to_subject'),
    path('teachers/api/', views.get_teachers_api, name='get_teachers_api'),
    path('subjects/<uuid:subject_id>/manage-teachers/', views.manage_subject_teachers, name='manage_subject_teachers'),
    path('subjects/assign-teacher-to-class/', views.assign_teacher_to_class_subject, name='assign_teacher_to_class_subject'),
    path('subjects/update-class-assignment/', views.update_class_assignment, name='update_class_assignment'),
    path('subjects/class-assignment/<int:assignment_id>/delete/', views.delete_class_assignment, name='delete_class_assignment'),


    path('results/', views.results_dashboard, name='results_dashboard'),
    path('results/upload/', views.upload_results, name='upload_results'),
    path('results/analysis/', views.results_analysis, name='results_analysis'),
    path('results/<uuid:result_id>/', views.result_detail, name='result_detail'),
    path('results/<uuid:result_id>/publish/', views.publish_results, name='publish_result'),
    path('results/<uuid:result_id>/delete/', views.delete_result, name='delete_result'),
    path('api/results/students/', views.get_students_for_results, name='get_students_for_results'),
    path('api/results/existing/', views.get_existing_results, name='get_existing_results'),
    path('api/results/publish-bulk/', views.publish_results, name='publish_results_bulk'),
    path('api/terms/', views.get_terms_for_academic_year, name='get_terms_for_academic_year'),
    path('results/analysis/export/', views.export_analysis_report, name='export_analysis_report'),
]