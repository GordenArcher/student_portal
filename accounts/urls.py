from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('users/<uuid:user_id>/update/', views.user_update, name='user_update'),
    path('users/<uuid:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # Teacher Profiles
    path('teachers/create/', views.register_teacher, name='teacher_create'),
    path('teachers/<int:teacher_id>/update/', views.teacher_update, name='teacher_update'),
    
    # Student Profiles
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:student_id>/update/', views.student_update, name='student_update'),
    
    # Staff Profiles
    path('staff/create/', views.staff_create, name='staff_create'),
    
    # JSON API Endpoints
    path('api/users/', views.user_api_list, name='user_api_list'),
    path('api/users/<uuid:user_id>/', views.user_api_detail, name='user_api_detail'),
    
    # Dashboards
        #Admin
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/teachers/', views.teacher_list, name='teachers_list'),

        #Teacher
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),

        #Student
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    
    # User actions
    path('users/<uuid:user_id>/reset-password/', views.reset_password, name='reset_password'),
    path('users/<uuid:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<uuid:user_id>/data/', views.get_user_data, name='get_user_data'),
    path('users/<uuid:user_id>/change-password/', views.change_password, name='change_password'),
]