from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from .models import User, TeacherProfile, StudentProfile, StaffProfile
from academics.models import Subject, ClassLevel, Term, Result, AcademicYear
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .utils.generateID import generate_teacher_id, generate_student_id
from core.views import get_recent_activities, get_teacher_workload
from django.core.exceptions import PermissionDenied
from django.db.models import Case, When, Q, Count, Avg, Max
from django.db import models




# ============ Authentication Views ============

@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'teacher':
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# ============ User Management Views ============

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
@transaction.atomic
def register_teacher(request):
    """API endpoint for registering teachers"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        phone_number = data.get("phone_number")
        gender = data.get("gender")
        password = data.get("password")
        date_of_birth = data.get("date_of_birth")
        profile_picture = request.FILES.get("profile_picture")
        employment_type = data.get("employment_type", "full_time")
        is_class_teacher = data.get("is_class_teacher") == "on" or data.get("is_class_teacher") == "true"
        class_teacher_of_id = data.get("class_teacher_of")
        subject_ids = data.getlist("subjects") if hasattr(data, 'getlist') else data.get("subjects", [])

        if not all([first_name, last_name, email]):
            return JsonResponse({
                'success': False, 
                'error': 'First name, last name, and email are required.'
            }, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A user with this email already exists.'
            }, status=400)
        
        employee_id = generate_teacher_id()

        user = User.objects.create_user(
            username=employee_id,
            email=email,
            password=password or "changeme123",
            first_name=first_name,
            last_name=last_name,
            role="teacher",
            phone_number=phone_number,
            gender=gender,
            date_of_birth=date_of_birth,
        )
        
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
        
        
        teacher_profile = TeacherProfile.objects.create(
            user=user,
            employee_id=employee_id,
            employment_type=employment_type,
            is_class_teacher=is_class_teacher,
            class_teacher_of=ClassLevel.objects.filter(id=class_teacher_of_id).first() if class_teacher_of_id else None
        )
        
        if subject_ids:
            if isinstance(subject_ids, str):
                import ast
                subject_ids = ast.literal_eval(subject_ids)
            subjects = Subject.objects.filter(id__in=subject_ids)
            teacher_profile.subjects.set(subjects)
        
        response_data = {
            'success': True,
            'message': f'Teacher {user.get_full_name()} registered successfully with ID {employee_id}.',
        }
        
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, response_data['message'])
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while registering teacher: {str(e)}'
        }, status=400)



@login_required
def user_list(request):
    """List all users with filtering and search"""
    users = User.objects.select_related(
        'teacher_profile', 'student_profile', 'staff_profile'
    ).all()
    
    # Filter by role
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    
    # Search
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'role': role,
        'search': search,
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
def user_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    
    context = {
        'user': user,
    }
    
    if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
        context['profile'] = user.teacher_profile
    elif user.role == 'student' and hasattr(user, 'student_profile'):
        context['profile'] = user.student_profile
    elif user.role == 'admin' and hasattr(user, 'staff_profile'):
        context['profile'] = user.staff_profile
    
    return render(request, 'accounts/user_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def user_update(request, user_id):
    """Update user details"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number')
            user.date_of_birth = request.POST.get('date_of_birth') or None
            user.gender = request.POST.get('gender') or None
            user.emergency_contact_name = request.POST.get('emergency_contact_name')
            user.emergency_contact_phone = request.POST.get('emergency_contact_phone')
            
            if request.FILES.get('profile_picture'):
                user.profile_picture = request.FILES['profile_picture']
            
            user.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_detail', user_id=user.id)
            
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    context = {
        'user': user,
        'genders': User.GENDER_CHOICES,
    }
    return render(request, 'accounts/user_form.html', context)


@login_required
@require_http_methods(["POST"])
def user_delete(request, user_id):
    """Delete a user"""
    user = get_object_or_404(User, id=user_id)
    
    try:
        username = user.username
        user.delete()
        messages.success(request, f'{username} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting user: {str(e)}')
    
    return redirect('user_list')


@login_required
@require_http_methods(["POST"])
def change_password(request, user_id):
    """Change user password"""
    try:
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if new_password != confirm_password:
            return JsonResponse({'success': False, 'error': 'Passwords do not match'}, status=400)
        
        if len(new_password) < 8:
            return JsonResponse({'success': False, 'error': 'Password must be at least 8 characters long'}, status=400)
        
        user.set_password(new_password)
        user.save()
        
        messages.success(request, f'Password for {user.get_full_name()} changed successfully!')
        
        return JsonResponse({'success': True, 'message': 'Password changed successfully!'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# ============ Teacher Profile Views ============


@login_required
def teacher_list(request):
    """List all teachers with filtering and pagination"""
    teachers = TeacherProfile.objects.select_related('user').prefetch_related('subjects')
    

    emp_type = request.GET.get('employment_type')
    if emp_type:
        teachers = teachers.filter(employment_type=emp_type)
    

    status = request.GET.get('status')
    if status == 'active':
        teachers = teachers.filter(is_active=True)
    elif status == 'inactive':
        teachers = teachers.filter(is_active=False)
    
    search = request.GET.get('search')
    if search:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Get counts for stats
    total_teachers = teachers.count()
    full_time_teachers = teachers.filter(employment_type='full_time').count()
    part_time_teachers = teachers.filter(employment_type='part_time').count()
    contract_teachers = teachers.filter(employment_type='contract').count()
    
    # Pagination
    paginator = Paginator(teachers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'employment_types': TeacherProfile.EMPLOYMENT_TYPE_CHOICES,
        'emp_type': emp_type,
        'search': search,
        'status': status,
        'total_teachers': total_teachers,
        'full_time_teachers': full_time_teachers,
        'part_time_teachers': part_time_teachers,
        'contract_teachers': contract_teachers,
    }
    return render(request, 'pages/admin_dashboard/teachers.html', {'context': context})


@login_required
def student_list(request):
    """List all students with filtering and pagination"""
    students = StudentProfile.objects.select_related('user', 'current_class')
    
    # Filter by class
    class_filter = request.GET.get('class')
    if class_filter:
        students = students.filter(current_class_id=class_filter)
    
    # Filter by active status
    status = request.GET.get('status')
    if status == 'active':
        students = students.filter(is_active=True)
    elif status == 'inactive':
        students = students.filter(is_active=False)
    
    # Search
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(student_id__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Get counts and classes for filters
    total_students = students.count()
    classes = ClassLevel.objects.all()
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'classes': classes,
        'class_filter': class_filter,
        'search': search,
        'status': status,
        'total_students': total_students,
    }
    return render(request, 'pages/admin_dashboard/students.html', {'context': context})


@login_required
@require_http_methods(["POST"])
def user_update(request, user_id):
    """Update an existing user"""
    try:
        user = get_object_or_404(User, id=user_id)
        data = request.POST
        files = request.FILES
        
        # Update basic user fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.phone_number = data.get('phone_number', user.phone_number)
        user.date_of_birth = data.get('date_of_birth') or user.date_of_birth
        user.gender = data.get('gender', user.gender)
        
        if files.get('profile_picture'):
            user.profile_picture = files['profile_picture']
        
        user.save()
        
        # Update profile based on role
        if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
            teacher_profile = user.teacher_profile
            teacher_profile.employment_type = data.get('employment_type', teacher_profile.employment_type)
            teacher_profile.is_class_teacher = data.get('is_class_teacher') == 'on'
            teacher_profile.class_teacher_of_id = data.get('class_teacher_of') or None
            teacher_profile.is_active = data.get('is_active') == 'on'
            teacher_profile.notes = data.get('notes', teacher_profile.notes)
            teacher_profile.save()
            
            # Update subjects
            subjects = data.getlist('subjects')
            if subjects:
                teacher_profile.subjects.set(subjects)
            
        elif user.role == 'student' and hasattr(user, 'student_profile'):
            student_profile = user.student_profile
            student_profile.current_class_id = data.get('current_class', student_profile.current_class_id)
            student_profile.academic_year = data.get('academic_year', student_profile.academic_year)
            student_profile.parent_full_name = data.get('parent_full_name', student_profile.parent_full_name)
            student_profile.parent_phone = data.get('parent_phone', student_profile.parent_phone)
            student_profile.parent_email = data.get('parent_email', student_profile.parent_email)
            student_profile.parent_address = data.get('parent_address', student_profile.parent_address)
            student_profile.emergency_contact_relation = data.get('emergency_contact_relation', student_profile.emergency_contact_relation)
            student_profile.is_active = data.get('is_active') == 'on'
            student_profile.notes = data.get('notes', student_profile.notes)
            student_profile.save()
        
        messages.success(request, f'User {user.get_full_name()} updated successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'User updated successfully!'})
        return redirect('teacher_list' if user.role == 'teacher' else 'student_list')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        messages.error(request, f'Error updating user: {str(e)}')
        return redirect('teacher_list')


@login_required
@require_http_methods(["DELETE", "POST"])
def user_delete(request, user_id):
    """Delete a user"""
    try:
        user = get_object_or_404(User, id=user_id)
        user_name = user.get_full_name()
        user_role = user.role
        
        user.delete()
        
        messages.success(request, f'User {user_name} deleted successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'User deleted successfully!'})
        return redirect('teacher_list' if user_role == 'teacher' else 'student_list')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        messages.error(request, f'Error deleting user: {str(e)}')
        return redirect('teacher_list')



@login_required
@require_http_methods(["POST"])
def reset_password(request, user_id):
    """Reset user password to default"""
    try:
        user = get_object_or_404(User, id=user_id)
        new_password = 'changeme123'
        user.set_password(new_password)
        user.save()
        
        messages.success(request, f'Password for {user.get_full_name()} reset to default!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Password reset successfully!'})
        return redirect('teacher_list' if user.role == 'teacher' else 'student_list')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        messages.error(request, f'Error resetting password: {str(e)}')
        return redirect('teacher_list')


@login_required
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    try:
        user = get_object_or_404(User, id=user_id)
        
        if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
            profile = user.teacher_profile
        elif user.role == 'student' and hasattr(user, 'student_profile'):
            profile = user.student_profile
        else:
            raise ValueError("User profile not found")
        
        profile.is_active = not profile.is_active
        profile.save()
        
        status = "activated" if profile.is_active else "deactivated"
        messages.success(request, f'User {user.get_full_name()} {status} successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'User {status} successfully!',
                'is_active': profile.is_active
            })
        return redirect('teacher_list' if user.role == 'teacher' else 'student_list')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        messages.error(request, f'Error toggling user status: {str(e)}')
        return redirect('teacher_list')


@login_required
def get_user_data(request, user_id):

    """Get user data for AJAX requests"""
    try:
        user = get_object_or_404(User, id=user_id)
        
        data = {
            'id': str(user.id),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'gender': user.gender,
            'role': user.role,
        }
        
        if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
            teacher_profile = user.teacher_profile
            data.update({
                'employee_id': teacher_profile.employee_id,
                'employment_type': teacher_profile.employment_type,
                'is_class_teacher': teacher_profile.is_class_teacher,
                'class_teacher_of': str(teacher_profile.class_teacher_of.id) if teacher_profile.class_teacher_of else None,
                'is_active': teacher_profile.is_active,
                'notes': teacher_profile.notes,
                'subjects': list(teacher_profile.subjects.values_list('id', flat=True)),
            })
        
        elif user.role == 'student' and hasattr(user, 'student_profile'):
            student_profile = user.student_profile
            data.update({
                'student_id': student_profile.student_id,
                'current_class': str(student_profile.current_class.id) if student_profile.current_class else None,
                'academic_year': student_profile.academic_year,
                'parent_full_name': student_profile.parent_full_name,
                'parent_phone': student_profile.parent_phone,
                'parent_email': student_profile.parent_email,
                'parent_address': student_profile.parent_address,
                'emergency_contact_relation': student_profile.emergency_contact_relation,
                'is_active': student_profile.is_active,
                'notes': student_profile.notes,
            })
        
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    


@login_required
@require_http_methods(["GET", "POST"])
def teacher_update(request, teacher_id):
    """Update teacher profile"""
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    
    if request.method == 'POST':
        try:
            teacher.employee_id = request.POST.get('employee_id')
            teacher.employment_type = request.POST.get('employment_type')
            teacher.is_class_teacher = request.POST.get('is_class_teacher') == 'on'
            teacher.is_active = request.POST.get('is_active') == 'on'
            teacher.notes = request.POST.get('notes')
            
            # Update subjects
            subject_ids = request.POST.getlist('subjects')
            teacher.subjects.set(subject_ids)
            
            # Update class teacher of
            class_id = request.POST.get('class_teacher_of')
            teacher.class_teacher_of_id = class_id if class_id else None
            
            teacher.save()
            messages.success(request, 'Teacher profile updated successfully!')
            return redirect('user_detail', user_id=teacher.user.id)
            
        except Exception as e:
            messages.error(request, f'Error updating teacher profile: {str(e)}')
    
    context = {
        'teacher': teacher,
        'subjects': Subject.objects.all(),
        'classes': ClassLevel.objects.all(),
        'employment_types': TeacherProfile.EMPLOYMENT_TYPE_CHOICES,
    }
    return render(request, 'accounts/teacher_form.html', context)


# ============ Student Profile Views ============

@login_required
def student_list(request):
    """List all students with filtering and pagination"""
    students = StudentProfile.objects.select_related('user', 'current_class')
    
    class_id = request.GET.get('class')
    if class_id:
        students = students.filter(current_class_id=class_id)
    
    status = request.GET.get('status')
    if status == 'active':
        students = students.filter(is_active=True)
    elif status == 'inactive':
        students = students.filter(is_active=False)
    
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(student_id__icontains=search)
        )
    
    total_students = students.count()
    active_students = students.filter(is_active=True).count()
    inactive_students = students.filter(is_active=False).count()
    
    class_counts = ClassLevel.objects.annotate(
        student_count=Count('students')
    ).values('name', 'student_count')
    

    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'classes': ClassLevel.objects.all(),
        'class_id': class_id,
        'status': status,
        'search': search,
        'total_students': total_students,
        'active_students': active_students,
        'inactive_students': inactive_students,
        'class_counts': list(class_counts),
    }
    return render(request, 'pages/admin_dashboard/students.html', {'context': context})



@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
@transaction.atomic
def student_create(request):
    """API endpoint for registering students"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        phone_number = data.get("phone_number")
        gender = data.get("gender")
        password = data.get("password")
        date_of_birth = data.get("date_of_birth")
        profile_picture = request.FILES.get("profile_picture")
        current_class_id = data.get("current_class")
        parent_full_name = data.get("parent_full_name")
        parent_phone = data.get("parent_phone")
        parent_email = data.get("parent_email")
        parent_address = data.get("parent_address")
        emergency_contact_relation = data.get("emergency_contact_relation")
        
        # Validation
        if not all([first_name, last_name]):
            return JsonResponse({
                'success': False, 
                'error': 'First name, last name, and email are required.'
            }, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A user with this email already exists.'
            }, status=400)
        

        student_id = generate_student_id()

        if User.objects.filter(username=student_id).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A user with this username already exists.'
            }, status=400)
        
        
 
        user = User.objects.create_user(
            username=student_id,
            email=email,
            password=password or "changeme123",
            first_name=first_name,
            last_name=last_name,
            role="student",
            phone_number=phone_number,
            gender=gender,
            date_of_birth=date_of_birth,
        )
        
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
        

        student_profile = StudentProfile.objects.create(
            user=user,
            student_id=student_id,
            current_class_id=current_class_id,
            parent_full_name=parent_full_name,
            parent_phone=parent_phone,
            parent_email=parent_email,
            parent_address=parent_address,
            emergency_contact_relation=emergency_contact_relation,
        )
        
        response_data = {
            'success': True,
            'message': f'Student {user.get_full_name()} registered successfully with ID {student_id}.',
        }
        
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, response_data['message'])
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while registering student: {str(e)}'
        }, status=500)
    


@login_required
@require_http_methods(["GET", "POST"])
def student_update(request, student_id):
    """Update student profile"""
    student = get_object_or_404(StudentProfile, id=student_id)
    
    if request.method == 'POST':
        try:
            student.student_id = request.POST.get('student_id')
            student.current_class_id = request.POST.get('current_class') or None
            student.parent_full_name = request.POST.get('parent_full_name')
            student.parent_phone = request.POST.get('parent_phone')
            student.parent_email = request.POST.get('parent_email')
            student.parent_address = request.POST.get('parent_address')
            student.emergency_contact_relation = request.POST.get('emergency_contact_relation')
            student.is_active = request.POST.get('is_active') == 'on'
            student.notes = request.POST.get('notes')
            
            student.save()
            messages.success(request, 'Student profile updated successfully!')
            return redirect('user_detail', user_id=student.user.id)
            
        except Exception as e:
            messages.error(request, f'Error updating student profile: {str(e)}')
    
    context = {
        'student': student,
        'classes': ClassLevel.objects.all(),
    }
    return render(request, 'accounts/student_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def staff_create(request):
    """Create staff profile"""
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id, role='admin')
            
            staff = StaffProfile.objects.create(
                user=user,
                staff_id=request.POST.get('staff_id'),
                staff_type=request.POST.get('staff_type'),
            )
            
            messages.success(request, 'Staff profile created successfully!')
            return redirect('user_detail', user_id=user.id)
            
        except Exception as e:
            messages.error(request, f'Error creating staff profile: {str(e)}')
    
    # Get users with admin role who don't have a profile
    available_staff = User.objects.filter(
        role='admin'
    ).exclude(
        staff_profile__isnull=False
    )
    
    context = {
        'available_staff': available_staff,
        'staff_types': StaffProfile.STAFF_TYPE_CHOICES,
    }
    return render(request, 'accounts/staff_form.html', context)


@login_required
def user_api_list(request):
    """JSON API for user list"""
    users = User.objects.all()
    
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    data = []
    for user in users[:100]:  # Limit to 100 results
        data.append({
            'id': str(user.id),
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
        })
    
    return JsonResponse({'users': data})


@login_required
def user_api_detail(request, user_id):
    """JSON API for user detail"""
    user = get_object_or_404(User, id=user_id)
    
    data = {
        'id': str(user.id),
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': user.role,
        'phone_number': user.phone_number,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
        'gender': user.gender,
        'age': user.age,
        'is_active': user.is_active,
    }
    
    return JsonResponse(data)


@login_required
def admin_dashboard(request):
    """Admin dashboard with comprehensive statistics and analytics"""
    
    total_users = User.objects.count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_students = User.objects.filter(role='student').count()
    total_staff = User.objects.filter(role='admin').count()
    
    active_students = StudentProfile.objects.filter(is_active=True).count()
    active_teachers = TeacherProfile.objects.filter(is_active=True).count()
    
    total_subjects = Subject.objects.filter(is_active=True).count()
    total_classes = ClassLevel.objects.filter(is_active=True).count()
    
    current_term = Term.objects.filter(is_current=True).first()
    recent_results = Result.objects.filter(date_uploaded__gte=timezone.now()-timedelta(days=30)).count()
    
    avg_score = Result.objects.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
    recent_students = StudentProfile.objects.filter(
        created_at__gte=timezone.now()-timedelta(days=30)
    ).count()
    
    class_distribution = ClassLevel.objects.filter(is_active=True).annotate(
        student_count=Count('students')
    ).values('name', 'student_count').order_by('-student_count')
    
    teacher_employment = TeacherProfile.objects.values('employment_type').annotate(
        count=Count('id')
    )

    top_students = []
    if current_term:
        top_students = Result.objects.filter(
            term=current_term
        ).values(
            'student__id',
            'student__first_name',
            'student__last_name',
            'student__student_profile__student_id',
            'student__student_profile__current_class__name'
        ).annotate(
            avg_score=Avg('score')
        ).order_by('-avg_score')[:5]
    
    subject_stats = Subject.objects.filter(
        results__isnull=False
    ).annotate(
        student_count=Count('results__student', distinct=True),
        avg_score=Avg('results__score'),
        pass_rate=Avg(
            Case(
                When(results__score__gte=50, then=1),
                default=0,
                output_field=models.FloatField()
            )
        ) * 100
    ).values('name', 'student_count', 'avg_score', 'pass_rate').order_by('-avg_score')[:4]
    
    # Teacher workload (based on assigned subjects)
    # More detailed workload data
    teacher_workload = get_teacher_workload()

    for teacher in teacher_workload:
        teacher['id'] = str(teacher['id'])

    recent_activities = get_recent_activities()

    core_subjects = Subject.objects.filter(category='core', is_active=True).count()
    elective_subjects = Subject.objects.filter(category='elective', is_active=True).count()
    
    context = {
        'total_users': total_users,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_staff': total_staff,
        'active_students': active_students,
        'active_teachers': active_teachers,
        'total_subjects': total_subjects,
        'total_classes': total_classes,
        
        'recent_results': recent_results,
        'avg_score': round(avg_score, 2),
        'recent_students': recent_students,
        'class_distribution': list(class_distribution),
        'teacher_employment': list(teacher_employment),
        'current_term': current_term,
        
        'top_students': list(top_students),
        'subject_stats': list(subject_stats),
        'teacher_workload': teacher_workload,
        'recent_activities': recent_activities,
        'core_subjects': core_subjects,
        'elective_subjects': elective_subjects,
    }

    return render(request, 'accounts/admin_dashboard.html', {'context': context})


@login_required
def teacher_dashboard(request):
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    subjects = Subject.objects.filter(
        classsubject__teacher=request.user
    ).distinct()

    classes_taught = ClassLevel.objects.filter(
        classsubject__teacher=request.user
    ).distinct()

    recent_results = Result.objects.filter(
        uploaded_by=request.user
    ).select_related('student', 'subject').order_by('-date_uploaded')[:5]

    total_students = StudentProfile.objects.filter(
        current_class__classsubject__teacher=request.user
    ).distinct().count()

    context = {
        'teacher': teacher_profile,
        'subjects': subjects,
        'classes_taught': classes_taught,
        'total_students': total_students,
        'recent_results': recent_results,
    }

    return render(request, 'accounts/teacher_dashboard.html', context)


@login_required
def student_dashboard(request):

    """Comprehensive student dashboard with all results and filters"""
    if request.user.role != 'student':
        return redirect('admin_dashboard')
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    # Get filter parameters
    academic_year_id = request.GET.get('academic_year')
    term_id = request.GET.get('term')
    
    # Base queryset for results
    results = Result.objects.filter(
        student=request.user,
        is_published=True
    ).select_related('subject', 'class_level', 'term', 'term__academic_year')
    
    # Apply filters
    if academic_year_id:
        results = results.filter(term__academic_year_id=academic_year_id)
    if term_id:
        results = results.filter(term_id=term_id)
    
    # Get available filters
    academic_years = AcademicYear.objects.all().order_by('-start_date')
    terms = Term.objects.all().order_by('-academic_year', 'start_date')
    
    # Group results by term
    results_by_term = {}
    for result in results:
        term_key = f"{result.term.name} - {result.term.academic_year.name}"
        if term_key not in results_by_term:
            results_by_term[term_key] = {
                'term': result.term,
                'results': []
            }
        results_by_term[term_key]['results'].append(result)
    
    # Calculate statistics
    total_results = results.count()
    average_score = results.aggregate(avg=Avg('score'))['avg'] or 0
    best_subject = results.order_by('-score').first()
    worst_subject = results.order_by('score').first()
    
    # Grade distribution
    grade_distribution = results.values('grade').annotate(
        count=Count('id')
    ).order_by('grade')
    
    # Subject performance
    subject_performance = results.values(
        'subject__name', 'subject__code'
    ).annotate(
        avg_score=Avg('score'),
        count=Count('id'),
        max_score=Max('score')
    ).order_by('-avg_score')
    
    # Recent results (last 5)
    recent_results = results.order_by('-date_uploaded')[:5]
    
    context = {
        'student': student_profile,
        'class_teacher': student_profile.class_teacher,
        'results_by_term': results_by_term,
        'recent_results': recent_results,
        'total_results': total_results,
        'average_score': round(average_score, 2),
        'best_subject': best_subject,
        'worst_subject': worst_subject,
        'grade_distribution': grade_distribution,
        'subject_performance': subject_performance,
        'academic_years': academic_years,
        'terms': terms,
        'current_filters': {
            'academic_year_id': academic_year_id,
            'term_id': term_id,
        }
    }
    
    return render(request, 'accounts/student_dashboard.html', {'context': context})



def get_classes_ajax(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            classes = ClassLevel.objects.all().values('id', 'name')
            classes_list = list(classes)
            return JsonResponse({
                'classes': classes_list
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def manage_results(request):
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # Subjects this teacher teaches based on class assignments
    subjects = Subject.objects.filter(
        classsubject__teacher=request.user,
        is_active=True
    ).distinct()

    # Classes this teacher teaches
    classes_taught = ClassLevel.objects.filter(
        classsubject__teacher=request.user
    ).distinct()

    # Results only for subjects this teacher teaches
    results = Result.objects.filter(
        subject__classsubject__teacher=request.user
    ).select_related(
        'student', 'subject', 'class_level', 'term', 'uploaded_by'
    ).order_by('-date_uploaded').distinct()

    # ---- Filtering ----
    subject_filter = request.GET.get('subject')
    class_filter = request.GET.get('class_level')
    term_filter = request.GET.get('term')
    academic_year_filter = request.GET.get('academic_year')

    if subject_filter:
        results = results.filter(subject_id=subject_filter)

    if class_filter:
        results = results.filter(
            student__student_profile__current_class_id=class_filter
        )

    if term_filter:
        results = results.filter(term_id=term_filter)

    if academic_year_filter:
        results = results.filter(academic_year=academic_year_filter)

    context = {
        'teacher': teacher_profile,
        'subjects': subjects,
        'classes_taught': classes_taught,
        'results': results,
        'terms': Term.objects.all(),
        'current_filters': {
            'subject': subject_filter,
            'class_level': class_filter,
            'term': term_filter,
            'academic_year': academic_year_filter,
        }
    }

    return render(request, 'pages/teacher_dashboard/manage_results.html', context)


@login_required
def my_classes(request):
    """Teacher's classes page"""
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    
    # Get classes taught by this teacher with subject count
    classes_taught = ClassLevel.objects.filter(
        subjects__teacher=request.user
    ).distinct().annotate(
        subject_count=Count('subjects', filter=Q(subjects__teacher=request.user)),
        student_count=Count('students', distinct=True)
    )

    print(teacher_profile)
    
    context = {
        'teacher': teacher_profile,
        'classes_taught': classes_taught,
    }
    
    return render(request, 'pages/teacher_dashboard/my_classes.html', context)


@login_required
def my_students(request):
    """Teacher's students page"""
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    
    # Get students taught by this teacher
    students = StudentProfile.objects.filter(
        current_class__subjects__teacher=request.user
    ).distinct().select_related('user', 'current_class')
    
    # Filter by class if specified
    class_filter = request.GET.get('class')
    if class_filter:
        students = students.filter(current_class_id=class_filter)
    
    # Get classes for filter dropdown
    classes_taught = ClassLevel.objects.filter(
        subjects__teacher=request.user
    ).distinct()
    
    context = {
        'teacher': teacher_profile,
        'students': students,
        'classes_taught': classes_taught,
        'current_class_filter': class_filter,
    }
    
    return render(request, 'pages/teacher_dashboard/my_students.html', context)


@login_required
def class_students_ajax(request, class_id):
    """Get students for a specific class via AJAX"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
            
            # Verify teacher teaches this class
            class_taught = get_object_or_404(
                ClassLevel, 
                id=class_id, 
                subjects__teacher=teacher_profile
            )
            
            students = StudentProfile.objects.filter(
                current_class=class_taught
            ).values('id', 'student_id', 'user__first_name', 'user__last_name')
            
            return JsonResponse({
                'success': True,
                'students': list(students)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def student_results_ajax(request, student_id):
    """Get student results via AJAX"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
            student = get_object_or_404(StudentProfile, id=student_id)
            
            # Verify teacher teaches this student
            if not student.current_class.subjects.filter(teacher=teacher_profile).exists():
                return JsonResponse({'error': 'Not authorized'}, status=403)
            
            results = student.result_set.filter(
                subject__teacher=teacher_profile
            ).select_related('subject', 'term', 'academic_year').values(
                'id', 'score', 'grade', 'date_uploaded',
                'subject__name', 'subject__code',
                'term__name', 'academic_year__name'
            )
            
            return JsonResponse({
                'success': True,
                'results': list(results)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)