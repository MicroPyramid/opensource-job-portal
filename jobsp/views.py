
from django.shortcuts import render, redirect

def login(request):
    """
    Handles user login view.
    GET: Display the login page
    POST: Redirect to the main login handler
    """
    if request.user.is_authenticated:
        # Redirect authenticated users to appropriate dashboard
        if hasattr(request.user, 'user_type'):
            if request.user.user_type == 'JS':
                return redirect('/')  # Job seeker dashboard
            elif request.user.user_type == 'REC':
                return redirect('/recruiter/dashboard/')  # Recruiter dashboard
        return redirect('/')
    
    # For GET requests, show the login page
    # For POST requests, the form will be handled by AJAX to /applicant/login/
    context = {
        'next': request.GET.get('next', ''),
    }
    
    return render(request, 'login.html', context)