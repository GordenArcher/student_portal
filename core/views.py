from django.shortcuts import render
from django.http.response import HttpResponse
from accounts.models import StudentProfile, TeacherProfile
from academics.models import Result, ClassSubject
from django.utils.timesince import timesince
from django.utils import timezone
from django.core.cache import cache

# Create your views here.

def home_page(request):

    return render(request, "Index.html")



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
            'icon': '📝',
            'color': '#dbeafe'
        })

    #Recently enrolled students
    for student in StudentProfile.objects.select_related('current_class').order_by('-created_at')[:5]:
        activities.append({
            'type': 'student_enrollment',
            'title': 'New student enrolled',
            'details': f"{student.user.get_full_name()} - {student.current_class.name if student.current_class else 'N/A'}",
            'time': timesince(student.created_at, timezone.now()) + " ago",
            'icon': '✅',
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
                'icon': '👨‍🏫',
                'color': '#ede9fe'
            })

            
    cache.set(cache_key, activities, 60)
    # Sort activities by time (newest first)
    activities_sorted = sorted(activities, key=lambda x: x['time'], reverse=False)

    return activities_sorted[:limit]
