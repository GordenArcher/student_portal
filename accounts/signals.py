from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, TeacherProfile, StudentProfile
from accounts.utils.generateID import generate_teacher_id, generate_student_id

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create related profile when a new User is created.
    """
    if created:
        if instance.role == 'teacher' and not hasattr(instance, 'teacher_profile'):
            TeacherProfile.objects.create(
                user=instance,
                employee_id=generate_teacher_id()
            )
        elif instance.role == 'student' and not hasattr(instance, 'student_profile'):
            StudentProfile.objects.create(
                user=instance,
                student_id=generate_student_id()
            )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save related profile when User is updated.
    """
    if instance.role == 'teacher' and hasattr(instance, 'teacher_profile'):
        instance.teacher_profile.save()
    elif instance.role == 'student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
