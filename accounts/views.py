from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
import json
from .models import User, TeacherProfile, StudentProfile, StaffProfile
from academics.models import Subject, ClassLevel, Term, Result
from django.utils import timezone
from datetime import timedelta


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
    
    # Add role-specific profile
    if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
        context['profile'] = user.teacher_profile
    elif user.role == 'student' and hasattr(user, 'student_profile'):
        context['profile'] = user.student_profile
    elif user.role == 'admin' and hasattr(user, 'staff_profile'):
        context['profile'] = user.staff_profile
    
    return render(request, 'accounts/user_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        try:
            # Create user
            user = User.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                password=request.POST.get('password'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                role=request.POST.get('role'),
                phone_number=request.POST.get('phone_number'),
                date_of_birth=request.POST.get('date_of_birth') or None,
                gender=request.POST.get('gender') or None,
            )
            
            # Handle profile picture
            if request.FILES.get('profile_picture'):
                user.profile_picture = request.FILES['profile_picture']
                user.save()
            
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('user_detail', user_id=user.id)
            
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    context = {
        'roles': User.ROLE_CHOICES,
        'genders': User.GENDER_CHOICES,
    }
    return render(request, 'accounts/user_form.html', context)


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


# ============ Teacher Profile Views ============

@login_required
def teacher_list(request):
    """List all teachers"""
    teachers = TeacherProfile.objects.select_related('user').prefetch_related('subjects')
    
    # Filter by employment type
    emp_type = request.GET.get('employment_type')
    if emp_type:
        teachers = teachers.filter(employment_type=emp_type)
    
    # Search
    search = request.GET.get('search')
    if search:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_id__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(teachers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'employment_types': TeacherProfile.EMPLOYMENT_TYPE_CHOICES,
        'emp_type': emp_type,
        'search': search,
    }
    return render(request, 'accounts/teacher_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def teacher_create(request):
    """Create teacher profile"""
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id, role='teacher')
            
            teacher = TeacherProfile.objects.create(
                user=user,
                employee_id=request.POST.get('employee_id'),
                employment_type=request.POST.get('employment_type'),
                is_class_teacher=request.POST.get('is_class_teacher') == 'on',
                notes=request.POST.get('notes'),
            )
            
            # Add subjects
            subject_ids = request.POST.getlist('subjects')
            if subject_ids:
                teacher.subjects.set(subject_ids)
            
            # Set class teacher of
            class_id = request.POST.get('class_teacher_of')
            if class_id:
                teacher.class_teacher_of_id = class_id
                teacher.save()
            
            messages.success(request, 'Teacher profile created successfully!')
            return redirect('user_detail', user_id=user.id)
            
        except Exception as e:
            messages.error(request, f'Error creating teacher profile: {str(e)}')
    
    # Get users with teacher role who don't have a profile
    available_teachers = User.objects.filter(
        role='teacher'
    ).exclude(
        teacher_profile__isnull=False
    )
    
    context = {
        'available_teachers': available_teachers,
        'subjects': Subject.objects.all(),
        'classes': ClassLevel.objects.all(),
        'employment_types': TeacherProfile.EMPLOYMENT_TYPE_CHOICES,
    }
    return render(request, 'accounts/teacher_form.html', context)


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
    """List all students"""
    students = StudentProfile.objects.select_related('user', 'current_class')
    
    # Filter by class
    class_id = request.GET.get('class')
    if class_id:
        students = students.filter(current_class_id=class_id)
    
    # Filter by active status
    is_active = request.GET.get('is_active')
    if is_active:
        students = students.filter(is_active=is_active == 'true')
    
    # Search
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(student_id__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'classes': ClassLevel.objects.all(),
        'class_id': class_id,
        'is_active': is_active,
        'search': search,
    }
    return render(request, 'accounts/student_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def student_create(request):
    """Create student profile"""
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id, role='student')
            
            student = StudentProfile.objects.create(
                user=user,
                student_id=request.POST.get('student_id'),
                current_class_id=request.POST.get('current_class') or None,
                parent_full_name=request.POST.get('parent_full_name'),
                parent_phone=request.POST.get('parent_phone'),
                parent_email=request.POST.get('parent_email'),
                parent_address=request.POST.get('parent_address'),
                emergency_contact_relation=request.POST.get('emergency_contact_relation'),
                notes=request.POST.get('notes'),
            )
            
            messages.success(request, 'Student profile created successfully!')
            return redirect('user_detail', user_id=user.id)
            
        except Exception as e:
            messages.error(request, f'Error creating student profile: {str(e)}')
    
    # Get users with student role who don't have a profile
    available_students = User.objects.filter(
        role='student'
    ).exclude(
        student_profile__isnull=False
    )
    
    context = {
        'available_students': available_students,
        'classes': ClassLevel.objects.all(),
    }
    return render(request, 'accounts/student_form.html', context)


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


# ============ Staff Profile Views ============

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


# ============ API/JSON Endpoints ============

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


# ============ Dashboard Views ============

@login_required
def admin_dashboard(request):
    """Admin dashboard with comprehensive statistics and analytics"""
    # Basic counts
    total_users = User.objects.count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_students = User.objects.filter(role='student').count()
    total_staff = User.objects.filter(role='admin').count()
    
    # Active profiles
    active_students = StudentProfile.objects.filter(is_active=True).count()
    active_teachers = TeacherProfile.objects.filter(is_active=True).count()
    
    # Academic data
    total_subjects = Subject.objects.filter(is_active=True).count()
    total_classes = ClassLevel.objects.filter(is_active=True).count()
    
    # Recent results data
    current_term = Term.objects.filter(is_current=True).first()
    recent_results = Result.objects.filter(date_uploaded__gte=timezone.now()-timedelta(days=30)).count()
    
    # Performance data
    avg_score = Result.objects.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
    # Recent activity
    recent_students = StudentProfile.objects.filter(
        created_at__gte=timezone.now()-timedelta(days=30)
    ).count()
    
    # Class distribution
    class_distribution = ClassLevel.objects.filter(is_active=True).annotate(
        student_count=Count('students')
    ).values('name', 'student_count')
    
    # Teacher distribution by employment type
    teacher_employment = TeacherProfile.objects.values('employment_type').annotate(
        count=Count('id')
    )
    
    context = {
        # Basic counts
        'total_users': total_users,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_staff': total_staff,
        'active_students': active_students,
        'active_teachers': active_teachers,
        'total_subjects': total_subjects,
        'total_classes': total_classes,
        
        # Analytics
        'recent_results': recent_results,
        'avg_score': round(avg_score, 2),
        'recent_students': recent_students,
        'class_distribution': list(class_distribution),
        'teacher_employment': list(teacher_employment),
        'current_term': current_term,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    """Teacher dashboard"""
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    
    context = {
        'teacher': teacher_profile,
        'subjects': teacher_profile.subjects.all(),
        'total_students': teacher_profile.total_students,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)


@login_required
def student_dashboard(request):
    """Student dashboard"""
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    context = {
        'student': student_profile,
        'class_teacher': student_profile.class_teacher,
    }
    return render(request, 'accounts/student_dashboard.html', context)