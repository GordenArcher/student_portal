from django.shortcuts import redirect

def redirect_to_dashboard(user):
    """Helper function to redirect users based on role"""
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'teacher':
        return redirect('teacher_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    else:
        # Fallback for unknown roles
        return redirect('home')
    