from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.core.validators import RegexValidator
from django.utils import timezone
from academics.models import Subject, ClassLevel


class User(AbstractUser):
    """
        Custom User model with roles: admin, teacher, student.
        UUID is used as primary key.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        """Return the full name of the user."""
        return self.get_full_name()
    
    @property
    def age(self):
        """Calculate age from date of birth."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class TeacherProfile(models.Model):
    """
        Profile for teachers with employee ID and subjects taught.
    """
    EMPLOYMENT_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('substitute', 'Substitute'),
    )

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='teacher_profile',
        limit_choices_to={'role': 'teacher'}
    )
    employee_id = models.CharField(max_length=20, unique=True, db_index=True)
    subjects = models.ManyToManyField(Subject, related_name='teachers', blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    is_class_teacher = models.BooleanField(default=False)
    class_teacher_of = models.ForeignKey(
        ClassLevel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='class_teacher'
    )
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teacher_profiles'
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'
        indexes = [
            models.Index(fields=['employee_id']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"
    
    @property
    def total_students(self):
        """Get total number of students taught by this teacher."""
        from django.db.models import Count
        return self.user.teacher_profile.subjects.aggregate(
            total_students=Count('classes__students', distinct=True)
        )['total_students'] or 0


class StudentProfile(models.Model):
    """
    Profile for students with student ID and class assignment.
    """
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile',
        limit_choices_to={'role': 'student'}
    )
    student_id = models.CharField(max_length=20, unique=True, db_index=True)
    current_class = models.ForeignKey(
        ClassLevel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='students'
    )
    academic_year = models.CharField(max_length=9, default='2024-2025')
    parent_full_name = models.CharField(max_length=100, blank=True, null=True)
    parent_phone = models.CharField(max_length=17, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    parent_address = models.TextField(blank=True, null=True)
    
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['current_class']),
            models.Index(fields=['academic_year']),
        ]
        unique_together = ['current_class']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"
    
    @property
    def class_teacher(self):
        """Get the class teacher for this student's class."""
        if self.current_class and hasattr(self.current_class, 'class_teacher'):
            return self.current_class.class_teacher
        return None
    
    @property
    def age(self):
        """Calculate student's age."""
        return self.user.age
    
    def save(self, *args, **kwargs):
        """Auto-generate roll number if not provided and class is set."""
        if self.current_class and not self.roll_number:
            last_student = StudentProfile.objects.filter(
                current_class=self.current_class
            ).order_by('-roll_number').first()
            self.roll_number = (last_student.roll_number + 1) if last_student and last_student.roll_number else 1
        super().save(*args, **kwargs)


class StaffProfile(models.Model):
    """
        Profile for add staff.
    """
    STAFF_TYPE_CHOICES = (
        ('administrative', 'Administrative'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        limit_choices_to={'role': 'admin'}
    )
    staff_id = models.CharField(max_length=20, unique=True)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPE_CHOICES)
    
    class Meta:
        db_table = 'staff_profiles'
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.staff_id}"