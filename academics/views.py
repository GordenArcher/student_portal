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

from .models import Subject, ClassLevel, AcademicYear, Term

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