from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth import logout

# decorator to ensure that only authenticated students can access certain views
def student_login(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')

        # check if the user has the 'userinfo' attribute (custom user model check)
        if not hasattr(request.user, 'userinfo'):
            logout(request)
            return redirect('login')

        # ensure that the user is a student
        if request.user.userinfo.user_type != 'student':
            return HttpResponseForbidden("You are not authorized to view this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

# decorator to ensure that only authenticated teachers can access certain views
def teacher_login(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')
        
        # check if the user has the 'userinfo' attribute (custom user model check)
        if not hasattr(request.user, 'userinfo'):
            logout(request)
            return redirect('index')
        
        # ensure that the user is a teacher
        if request.user.userinfo.user_type != 'teacher':
            return HttpResponseForbidden("You are not authorized to view this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

# decorator to check login status and redirect accordingly
def check_login(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # if the user is already authenticated
        if request.user.is_authenticated:
            # check if the user has the 'userinfo' attribute (custom user model check)
            if not hasattr(request.user, 'userinfo'):
                logout(request)
                return redirect('login')
            
            # redirect based on user type (teacher or student)
            return redirect('teacher-home' if request.user.userinfo.user_type == 'teacher' else 'student-home')
            
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view