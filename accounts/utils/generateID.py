from accounts.models import TeacherProfile, StudentProfile
from django.db.models import Max


def generate_teacher_id():
    """
    Generate unique Teacher ID in the format: NSA-TCH-0001
    """
    last_id = TeacherProfile.objects.aggregate(last=Max('employee_id'))['last']
    if last_id:
        try:
            num = int(last_id.split('-')[-1])
        except ValueError:
            num = 0
    else:
        num = 0
    new_id = f"NSA-TCH-{num + 1:04d}"
    return new_id


def generate_student_id():
    """
    Generate unique Student ID in the format: NSA-STU-0001
    """
    last_id = StudentProfile.objects.aggregate(last=Max('student_id'))['last']
    if last_id:
        try:
            num = int(last_id.split('-')[-1])
        except ValueError:
            num = 0
    else:
        num = 0
    new_id = f"NSA-STU-{num + 1:04d}"
    return new_id
