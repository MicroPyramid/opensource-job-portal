from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.http import require_http_methods
from datetime import datetime
from psite.forms import AuthenticationForm, UserEmailRegisterForm
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
import json
import logging
import boto3
import random
from datetime import timezone
from peeldb.models import User, UserEmail
from pjob.views import save_codes_and_send_mail, add_other_location_to_user

# Set up logger
logger = logging.getLogger(__name__)


def user_login(request):
    """
    Handles user login view.
    GET: Display the login page
    POST: Process login via AJAX and return JSON response
    """
    if request.user.is_authenticated:
        # Redirect authenticated users to appropriate dashboard
        if hasattr(request.user, 'user_type'):
            if request.user.user_type == 'JS':
                return redirect('/')  # Job seeker dashboard
            elif request.user.user_type in ['RR', 'RA', 'AA', 'AR']:
                return redirect('/recruiter/dashboard/')  # Recruiter dashboard
        return redirect('/')
    
    if request.method == 'POST':
        # Handle AJAX login requests via email/password
        try:
            validate_user = AuthenticationForm(request.POST)
            
            if validate_user.is_valid():
                email = request.POST.get("email")
                password = request.POST.get("password")
                remember_me = request.POST.get("remember_me")
                
                # Authenticate user
                usr = authenticate(username=email, password=password)
                
                if usr:
                    if usr.is_active:
                        usr.last_login = datetime.now()
                        usr.save()
                        auth_login(request, usr)
                        
                        # Set session expiry based on remember me
                        if not remember_me:
                            request.session.set_expiry(0)  # Session expires when browser closes
                        
                        # Determine redirect URL based on user type
                        redirect_url = "/profile/"
                        if hasattr(usr, 'user_type'):
                            if usr.user_type == 'JS':
                                redirect_url = "/"
                            elif usr.user_type in ['RR', 'RA', 'AA', 'AR']:
                                redirect_url = "/recruiter/dashboard/"
                        
                        data = {
                            "error": False, 
                            "message": "Logged in successfully",
                            "redirect_url": redirect_url
                        }
                    else:
                        data = {
                            "error": True,
                            "message": "Your account is inactive. Please contact support.",
                        }
                else:
                    data = {
                        "error": True,
                        "message": "Invalid email or password. Please try again.",
                    }
            else:
                # Form validation errors
                error_messages = []
                for field, errors in validate_user.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                data = {
                    "error": True, 
                    "message": "Please correct the following errors: " + "; ".join(error_messages)
                }
            
            return JsonResponse(data)
            
        except Exception as e:
            logger.error(f"Exception during login: {str(e)}", exc_info=True)
            data = {
                "error": True,
                "message": "An error occurred during login. Please try again."
            }
            return JsonResponse(data, status=500)
    
    # For GET requests, show the login page
    context = {
        'next': request.GET.get('next', ''),
    }
    
    return render(request, 'login.html', context)


def user_register(request):
    """
    Handles user registration view.
    GET: Display the registration page
    POST: Process registration via AJAX and return JSON response
    """
    if request.user.is_authenticated:
        # Redirect authenticated users to appropriate dashboard
        if hasattr(request.user, 'user_type'):
            if request.user.user_type == 'JS':
                return redirect('/')  # Job seeker dashboard
            elif request.user.user_type in ['RR', 'RA', 'AA', 'AR']:
                return redirect('/recruiter/dashboard/')  # Recruiter dashboard
        return redirect('/')
    
    if request.method == 'POST':
        # Handle AJAX registration requests
        try:
            validate_user = UserEmailRegisterForm(request.POST, request.FILES)
            
            if validate_user.is_valid():
                email = request.POST.get("email")
                password = request.POST.get("password")
                registered_from = request.POST.get("register_from", "Email")
                
                # Check if user already exists
                if not (
                    User.objects.filter(email__iexact=email)
                    or User.objects.filter(username__iexact=email)
                ):
                    # Create new user
                    user = User.objects.create(
                        username=email,
                        email=email,
                        user_type="JS",
                        registered_from=registered_from,
                    )
                    
                    # Save form data to user instance
                    user_form = UserEmailRegisterForm(request.POST, instance=user)
                    user = user_form.save(commit=False)
                    
                    # Handle other location if provided
                    if request.POST.get("other_loc"):
                        add_other_location_to_user(user, request)
                    
                    # Set user preferences
                    user.email_notifications = (
                        request.POST.get("email_notifications") == "on"
                    )
                    user.set_password(password)
                    user.referer = request.session.get("referer", "")
                    user.save()
                    
                    # Send activation email
                    save_codes_and_send_mail(user, request, password)
                    
                    # Handle resume upload if provided
                    if "resume" in request.FILES:
                        try:
                            s3_client = boto3.client(
                                's3',
                                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                            )
                            random_string = "".join(
                                random.choice("0123456789ABCDEF") for i in range(3)
                            )
                            user_id = str(user.id) + str(random_string)
                            path = (
                                "resume/"
                                + user_id
                                + "/"
                                + request.FILES["resume"]
                                .name.replace(" ", "-")
                                .encode("ascii", "ignore")
                                .decode("ascii")
                            )
                            s3_client.put_object(
                                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                Key=path,
                                Body=request.FILES["resume"].read(),
                                ACL='public-read'
                            )
                            user.resume = path
                            user.profile_updated = datetime.now(timezone.utc)
                            user.save()
                        except Exception as e:
                            logger.error(f"Resume upload failed: {str(e)}", exc_info=True)
                    
                    # Authenticate and login user
                    registered_user = authenticate(username=user.username)
                    if registered_user:
                        auth_login(request, registered_user)
                    
                    # Create primary email record
                    UserEmail.objects.create(user=user, email=email, is_primary=True)
                    
                    # Determine redirect URL
                    redirect_url = reverse("user_reg_success")
                    if request.POST.get("detail_page"):
                        redirect_url = request.POST.get("detail_page")
                    
                    data = {
                        "error": False,
                        "message": "Registration successful! Please check your email to activate your account.",
                        "redirect_url": redirect_url,
                    }
                    return JsonResponse(data)
                else:
                    data = {
                        "error": True,
                        "message": "User with this email already exists.",
                    }
                    return JsonResponse(data)
            else:
                # Form validation errors
                error_messages = []
                for field, errors in validate_user.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                data = {
                    "error": True, 
                    "message": "Please correct the following errors: " + "; ".join(error_messages)
                }
                return JsonResponse(data)
            
        except Exception as e:
            logger.error(f"Exception during registration: {str(e)}", exc_info=True)
            data = {
                "error": True,
                "message": "An error occurred during registration. Please try again."
            }
            return JsonResponse(data, status=500)
    
    # For GET requests, show the registration page
    context = {
        'next': request.GET.get('next', ''),
    }
    
    return render(request, 'register.html', context)