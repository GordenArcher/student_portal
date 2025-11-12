# academics/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
import json
from accounts.models import User
from .models import Subject, ClassLevel, AcademicYear, Term
import ast

@login_required
def subject_list(request):
    """List all subjects with filtering and pagination"""
    subjects = Subject.objects.all()
    
    category = request.GET.get('category')
    if category:
        subjects = subjects.filter(category=category)
    
    is_active = request.GET.get('is_active')
    if is_active:
        subjects = subjects.filter(is_active=is_active == 'true')
    
    search = request.GET.get('search')
    if search:
        subjects = subjects.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(description__icontains=search)
        )
    
    total_subjects = subjects.count()
    core_subjects = subjects.filter(category='core').count()
    elective_subjects = subjects.filter(category='elective').count()
    active_subjects = subjects.filter(is_active=True).count()
    
    paginator = Paginator(subjects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category': category,
        'is_active': is_active,
        'search': search,
        'total_subjects': total_subjects,
        'core_subjects': core_subjects,
        'elective_subjects': elective_subjects,
        'active_subjects': active_subjects,
        'categories': Subject.SUBJECT_CATEGORY_CHOICES,
    }

    return render(request, 'pages/admin_dashboard/subject_lists.html', {'context': context})



@login_required
@require_http_methods(["POST"])
@transaction.atomic
def subject_create(request):
    """API endpoint for creating subjects"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        name = data.get("name")
        code = data.get("code")
        description = data.get("description")
        category = data.get("category", "core")
        is_active = data.get("is_active") == "true" or data.get("is_active") == "on"
        teacher_id = data.get("teacher")
        
        if not all([name, code]):
            return JsonResponse({
                'success': False, 
                'error': 'Name and code are required.'
            }, status=400)
        
        if Subject.objects.filter(code=code).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A subject with this code already exists.'
            }, status=400)
        
        subject = Subject.objects.create(
            name=name,
            code=code,
            description=description,
            category=category,
            is_active=is_active,
            teacher_id=teacher_id if teacher_id else None,
        )
        
        response_data = {
            'success': True,
            'message': f'Subject {name} created successfully.'
        }
        
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, response_data['message'])
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while creating subject: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def subject_update(request, subject_id):
    """API endpoint for updating subjects"""
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        name = data.get("name")
        code = data.get("code")
        description = data.get("description")
        category = data.get("category")
        is_active = data.get("is_active") == "true" or data.get("is_active") == "on"
        teacher_id = data.get("teacher")
        
        if code != subject.code and Subject.objects.filter(code=code).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A subject with this code already exists.'
            }, status=400)
        
        subject.name = name
        subject.code = code
        subject.description = description
        subject.category = category
        subject.is_active = is_active
        subject.teacher_id = teacher_id if teacher_id else None
        subject.save()
        
        response_data = {
            'success': True,
            'message': f'Subject {name} updated successfully.',
        }
        
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, response_data['message'])
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while updating subject: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["DELETE", "POST"])
def subject_delete(request, subject_id):
    """Delete a subject"""
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        subject_name = subject.name
        subject.delete()
        
        response_data = {
            'success': True,
            'message': f'Subject {subject_name} deleted successfully.',
        }
        
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, response_data['message'])
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while deleting subject: {str(e)}'
        }, status=400)



@login_required
def class_list(request):
    """List all classes with filtering and pagination"""
    classes = ClassLevel.objects.all()
    
    is_active = request.GET.get('is_active')
    if is_active:
        classes = classes.filter(is_active=is_active == 'true')
    
    search = request.GET.get('search')
    if search:
        classes = classes.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(description__icontains=search)
        )
    
    total_classes = classes.count()
    active_classes = classes.filter(is_active=True).count()
    total_capacity = sum(cls.capacity for cls in classes)
    total_students = sum(cls.current_students_count for cls in classes)
    
    paginator = Paginator(classes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'is_active': is_active,
        'search': search,
        'total_classes': total_classes,
        'active_classes': active_classes,
        'total_capacity': total_capacity,
        'total_students': total_students,
    }
    return render(request, 'pages/admin_dashboard/class_list.html', {'context': context})


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def class_create(request):
    """API endpoint for creating classes"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        name = data.get("name")
        code = data.get("code")
        description = data.get("description")
        capacity = data.get("capacity", 30)
        display_order = data.get("display_order", 0)
        is_active = data.get("is_active") == "true" or data.get("is_active") == "on"
        form_teacher_id = data.get("form_teacher")
        subject_ids = data.getlist("subjects") if hasattr(data, 'getlist') else data.get("subjects", [])
        
        if not name:
            return JsonResponse({
                'success': False, 
                'error': 'Name is required.'
            }, status=400)
        
        if ClassLevel.objects.filter(name=name).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A class with this name already exists.'
            }, status=400)
        
        if code and ClassLevel.objects.filter(code=code).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A class with this code already exists.'
            }, status=400)
        
        class_level = ClassLevel.objects.create(
            name=name,
            code=code,
            description=description,
            capacity=capacity,
            display_order=display_order,
            is_active=is_active,
            form_teacher_id=form_teacher_id if form_teacher_id else None,
        )
        
        if subject_ids:
            if isinstance(subject_ids, str):
                import ast
                subject_ids = ast.literal_eval(subject_ids)
            subjects = Subject.objects.filter(id__in=subject_ids)
            class_level.subjects.set(subjects)
        
        response_data = {
            'success': True,
            'message': f'Class {name} created successfully.',
            'class_level': {
                'id': str(class_level.id),
                'name': class_level.name,
                'code': class_level.code,
                'capacity': class_level.capacity,
                'is_active': class_level.is_active,
            }
        }
        
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, response_data['message'])
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while creating class: {str(e)}'
        }, status=400)



@login_required
@require_http_methods(["POST"])
@transaction.atomic
def class_update(request, class_id):
    """API endpoint for updating classes"""
    try:
        class_level = get_object_or_404(ClassLevel, id=class_id)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        name = data.get("name")
        code = data.get("code")
        description = data.get("description")
        capacity = data.get("capacity")
        display_order = data.get("display_order")
        is_active = data.get("is_active") == "true" or data.get("is_active") == "on"
        form_teacher_id = data.get("form_teacher")
        subject_ids = data.getlist("subjects") if hasattr(data, 'getlist') else data.get("subjects", [])
        
        if name != class_level.name and ClassLevel.objects.filter(name=name).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A class with this name already exists.'
            }, status=400)
        
        if code != class_level.code and ClassLevel.objects.filter(code=code).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A class with this code already exists.'
            }, status=400)
        
        class_level.name = name
        class_level.code = code
        class_level.description = description
        class_level.capacity = capacity
        class_level.display_order = display_order
        class_level.is_active = is_active
        class_level.form_teacher_id = form_teacher_id if form_teacher_id else None
        class_level.save()
        
        if subject_ids:
            if isinstance(subject_ids, str):
                import ast
                subject_ids = ast.literal_eval(subject_ids)
            subjects = Subject.objects.filter(id__in=subject_ids)
            class_level.subjects.set(subjects)
        
        response_data = {
            'success': True,
            'message': f'Class {name} updated successfully.',
        }
        
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, response_data['message'])
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while updating class: {str(e)}'
        }, status=400)



@login_required
@require_http_methods(["DELETE", "POST"])
def class_delete(request, class_id):
    """Delete a class"""
    try:
        class_level = get_object_or_404(ClassLevel, id=class_id)
        class_name = class_level.name
        
        # Check if class has students
        if class_level.students.exists():
            return JsonResponse({
                'success': False, 
                'error': f'Cannot delete {class_name} because it has students assigned. Please reassign students first.'
            }, status=400)
        
        class_level.delete()
        
        response_data = {
            'success': True,
            'message': f'Class {class_name} deleted successfully.',
        }
        
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, response_data['message'])
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while deleting class: {str(e)}'
        }, status=400)



@login_required
@require_http_methods(["GET"])
def get_subject_data(request, subject_id):
    """Get subject data for AJAX requests"""
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        
        data = {
            'id': str(subject.id),
            'name': subject.name,
            'code': subject.code,
            'description': subject.description,
            'category': subject.category,
            'is_active': subject.is_active,
            'teacher': str(subject.teacher.id) if subject.teacher else None,
            'teacher_name': subject.teacher.get_full_name() if subject.teacher else None,
            'created_at': subject.created_at.isoformat(),
            'updated_at': subject.updated_at.isoformat(),
        }
        
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def get_class_data(request, class_id):
    """Get class data for AJAX requests"""
    try:
        class_level = get_object_or_404(ClassLevel, id=class_id)
        
        data = {
            'id': str(class_level.id),
            'name': class_level.name,
            'code': class_level.code,
            'description': class_level.description,
            'capacity': class_level.capacity,
            'display_order': class_level.display_order,
            'is_active': class_level.is_active,
            'form_teacher': str(class_level.form_teacher.id) if class_level.form_teacher else None,
            'form_teacher_name': class_level.form_teacher.get_full_name() if class_level.form_teacher else None,
            'current_students_count': class_level.current_students_count,
            'available_seats': class_level.available_seats,
            'subjects': list(class_level.subjects.values('id', 'name', 'code')),
            'created_at': class_level.created_at.isoformat(),
            'updated_at': class_level.updated_at.isoformat(),
        }
        
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def get_teachers_list(request):
    """Get list of teachers for dropdowns"""
    try:
        teachers = User.objects.filter(
            role='teacher',
            teacher_profile__is_active=True
        ).select_related('teacher_profile').values(
            'id', 'first_name', 'last_name', 'email', 'teacher_profile__employee_id'
        )
        
        teachers_list = list(teachers)
        return JsonResponse({'success': True, 'teachers': teachers_list})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def get_subjects_list(request):
    """Get list of subjects for dropdowns"""
    try:
        subjects = Subject.objects.filter(is_active=True).values('id', 'name', 'code')
        subjects_list = list(subjects)
        return JsonResponse({'success': True, 'subjects': subjects_list})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def assign_subjects_to_class(request, class_id):
    """API endpoint for assigning subjects to a class"""
    try:
        class_level = get_object_or_404(ClassLevel, id=class_id)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        subject_ids = data.getlist("subjects") if hasattr(data, 'getlist') else data.get("subjects", [])
        
        if isinstance(subject_ids, str):
            subject_ids = ast.literal_eval(subject_ids)
        
        subjects = Subject.objects.filter(id__in=subject_ids)
        
        class_level.subjects.set(subjects)
        
        response_data = {
            'success': True,
            'message': f'Successfully updated subjects for {class_level.name}.',
            'subjects_count': subjects.count()
        }
        
        return JsonResponse(response_data)
        

    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while updating class subjects: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def assign_teacher_to_class(request, class_id):
    """API endpoint for assigning teacher to a class"""
    try:
        class_level = get_object_or_404(ClassLevel, id=class_id)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        teacher_id = data.get("form_teacher")
        
        class_level.form_teacher_id = teacher_id if teacher_id else None
        class_level.save()
        
        teacher_name = class_level.form_teacher.get_full_name() if class_level.form_teacher else "No teacher"
        
        response_data = {
            'success': True,
            'message': f'Successfully assigned {teacher_name} to {class_level.name}.',
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'An error occurred while assigning teacher: {str(e)}'
        }, status=400)