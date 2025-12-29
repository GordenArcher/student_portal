from django.shortcuts import render
from django.http.response import HttpResponse
from accounts.models import StudentProfile, TeacherProfile
from academics.models import Result, ClassSubject
from django.utils.timesince import timesince
from django.utils import timezone
from django.core.cache import cache
from accounts.models import User
from django.db.models import Count, Q
from collections import defaultdict
from collections import defaultdict

# Create your views here.

def home_page(request):

    return render(request, "Index.html")


def contact_page(request):

    return render(request, "contact.html")



def get_recent_activities(limit=10):
    """Build a recent activity feed dynamically."""

    cache_key = f'recent_activities_{limit}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    activities = []

    # Recently uploaded results
    for result in Result.objects.select_related('student', 'subject', 'class_level').order_by('-date_uploaded')[:5]:
        activities.append({
            'type': 'result_upload',
            'title': 'Results uploaded',
            'details': f"{result.subject.name} - {result.class_level.name}",
            'time': timesince(result.date_uploaded, timezone.now()) + " ago",
            'icon': 'bi-upload',
            'color': '#dbeafe'
        })

    #Recently enrolled students
    for student in StudentProfile.objects.select_related('current_class').order_by('-created_at')[:5]:
        activities.append({
            'type': 'student_enrollment',
            'title': 'New student enrolled',
            'details': f"{student.user.get_full_name()} - {student.current_class.name if student.current_class else 'N/A'}",
            'time': timesince(student.created_at, timezone.now()) + " ago",
            'icon': 'bi-person-plus',
            'color': '#d1fae5'
        })

    # Recently assigned teachers to classes
    for cs in ClassSubject.objects.select_related('class_level', 'teacher', 'subject').order_by('-id')[:5]:
        if cs.teacher:
            activities.append({
                'type': 'teacher_assignment',
                'title': 'Teacher assigned',
                'details': f"{cs.teacher.get_full_name()} to {cs.subject.name} ({cs.class_level.name})",
                'time': "recently",  # You can add timestamp if you track assignment creation
                'icon': 'bi-person-badge',
                'color': '#ede9fe'
            })

            
    cache.set(cache_key, activities, 60)
    # Sort activities by time (newest first)
    activities_sorted = sorted(activities, key=lambda x: x['time'], reverse=False)

    return activities_sorted[:limit]





def get_teacher_workload():
    """Get teacher workload data - handles both relationship scenarios"""
    
    # Method 1: Try via User -> ClassSubject relationship (using the correct related_name)
    try:
        teacher_workload = User.objects.filter(
            role='teacher',
            is_active=True
        ).annotate(
            total_assignments=Count('assigned_class_subjects', distinct=True),
            total_subjects=Count('assigned_class_subjects__subject', distinct=True),
            total_classes=Count('assigned_class_subjects__class_level', distinct=True)
        ).values(
            'id',
            'first_name',
            'last_name', 
            'total_assignments',
            'total_subjects',
            'total_classes'
        ).order_by('-total_assignments')[:6]
        
        # Convert to list and filter out teachers with no assignments
        workload_list = list(teacher_workload)
        workload_list = [teacher for teacher in workload_list if teacher['total_assignments'] > 0]
        
        if workload_list:
            print(f" Method 1 successful: Found {len(workload_list)} teachers with assignments")
            print(workload_list)
            return workload_list
        else:
            print(" Method 1: No teachers with assignments found")
    except Exception as e:
        print(f" Method 1 failed: {e}")
    
    # Method 2: Direct query from ClassSubject (most reliable)
    try:
        class_assignments = ClassSubject.objects.filter(
            teacher__isnull=False,
            teacher__is_active=True
        ).select_related('teacher', 'subject', 'class_level')
        
        print(f"Method 2: Found {class_assignments.count()} ClassSubject records with teachers")
        
        workload_data = defaultdict(lambda: {
            'id': None,
            'first_name': '',
            'last_name': '',
            'total_assignments': 0,
            'total_subjects': set(),
            'total_classes': set()
        })
        
        for assignment in class_assignments:
            teacher_id = assignment.teacher.id
            workload_data[teacher_id]['id'] = teacher_id
            workload_data[teacher_id]['first_name'] = assignment.teacher.first_name
            workload_data[teacher_id]['last_name'] = assignment.teacher.last_name
            workload_data[teacher_id]['total_assignments'] += 1
            workload_data[teacher_id]['total_subjects'].add(assignment.subject.id)
            workload_data[teacher_id]['total_classes'].add(assignment.class_level.id)
        
        # Convert to list format
        result = []
        for teacher_id, data in workload_data.items():
            result.append({
                'id': data['id'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'total_assignments': data['total_assignments'],
                'total_subjects': len(data['total_subjects']),
                'total_classes': len(data['total_classes'])
            })
        
        result = sorted(result, key=lambda x: x['total_assignments'], reverse=True)[:6]
        
        if result:
            print(f" Method 2 successful: Found {len(result)} teachers with assignments")
            return result
        else:
            print(" Method 2: No teachers with assignments found")
            
    except Exception as e:
        print(f" Method 2 failed: {e}")
    
    # Method 3: Fallback - check if there are any ClassSubject records at all
    try:
        total_class_subjects = ClassSubject.objects.count()
        class_subjects_with_teachers = ClassSubject.objects.filter(teacher__isnull=False).count()
        total_teachers = User.objects.filter(role='teacher', is_active=True).count()
        
        print(f" Debug Info:")
        print(f"   - Total ClassSubject records: {total_class_subjects}")
        print(f"   - ClassSubject records with teachers: {class_subjects_with_teachers}")
        print(f"   - Total active teachers: {total_teachers}")
        
        # If there are ClassSubject records but no teachers assigned
        if total_class_subjects > 0 and class_subjects_with_teachers == 0:
            print("💡 Hint: ClassSubject records exist but no teachers are assigned to them")
            
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    # Return empty list if all methods fail
    return []