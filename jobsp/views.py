from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.utils import timezone
from zoneinfo import ZoneInfo
from dashboard.tasks import send_email
from psite.forms import AuthenticationForm, ForgotPassForm, UserEmailRegisterForm, UserPassChangeForm
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
import json
import logging
import boto3
import random
from peeldb.models import User, UserEmail
from django.template import loader
from pjob.views import save_codes_and_send_mail, add_other_location_to_user
from django.utils.crypto import get_random_string

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
                        auth_login(request, usr)
                        
                        # Set session expiry based on remember me
                        if not remember_me:
                            request.session.set_expiry(0)  # Browser close
                        else:
                            request.session.set_expiry(1209600)  # 2 weeks
                        
                        # Determine redirect URL
                        redirect_url = request.POST.get('next', '/')
                        if hasattr(usr, 'user_type'):
                            if usr.user_type == 'JS':
                                redirect_url = '/'
                            elif usr.user_type in ['RR', 'RA', 'AA', 'AR']:
                                redirect_url = '/recruiter/dashboard/'
                        
                        data = {
                            "error": False,
                            "message": "Login successful!",
                            "redirect_url": redirect_url,
                        }
                    else:
                        data = {
                            "error": True,
                            "message": "Your account is not active. Please contact support.",
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
    print("User Registration View Called")
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
                        add_other_location_to_user(request, user)
                    
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
                            # AWS S3 upload logic
                            s3_client = boto3.client(
                                's3',
                                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                region_name='us-east-1'
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
                            user.profile_updated = timezone.now()
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



def forgot_password(request):
    """
    Handles forgot password functionality.
    GET: Display the forgot password page
    POST: Process password reset request via AJAX
    """
    if request.method == 'POST':
        try:
            form_valid = ForgotPassForm(request.POST)
            if form_valid.is_valid():
                email = request.POST.get("email")
                user = User.objects.filter(email=email).first()
                
                if user and (user.is_recruiter or user.is_agency_admin):
                    data = {
                        "error": True,
                        "message": "User Already registered as a Recruiter",
                    }
                    return JsonResponse(data)
                
                if user:
                    # Generate new temporary password
                    user.password_reset_token = get_random_string(length=32)
                    user.password_reset_token_created_at = timezone.now()
                    user.save()
                    
                    # Prepare email content
                    temp = loader.get_template("email/forgot_password.html")
                    subject = "Password Reset - PeelJobs"
                    mto = email
                    url = (
                        request.scheme
                        + "://"
                        + request.META["HTTP_HOST"]
                        + "/set-password/"
                        + str(user.id)
                        + "/"
                        + str(user.password_reset_token)
                        + "/"
                    )
                    c = {"user": user, "redirect_url": url}
                    rendered = temp.render(c)
                    
                    # Send email using Celery task
                    logger.info(f"Sending password reset email to: {mto}")
                    try:
                        send_email.delay(mto, subject, rendered)
                        logger.info(f"Password reset email task queued successfully for: {mto}")
                    except Exception as e:
                        logger.error(f"Failed to queue email task: {str(e)}", exc_info=True)
                        # Fallback: send email directly if Celery is not available
                        from django.core.mail import EmailMessage
                        msg = EmailMessage(subject, rendered, settings.DEFAULT_FROM_EMAIL, [mto])
                        msg.content_subtype = "html"
                        msg.send()
                        logger.info(f"Password reset email sent directly for: {mto}")
                    
                    data = {"error": False, "message": "Password reset link sent successfully!", "redirect_url": "/"}
                else:
                    data = {
                        "error": True,
                        "message": "User doesn't exist with this Email",
                    }
                return JsonResponse(data)
            else:
                data = {"error": True, "message": form_valid.errors}
                return JsonResponse(data)
                
        except Exception as e:
            logger.error(f"Exception during password reset: {str(e)}", exc_info=True)
            data = {
                "error": True,
                "message": "An error occurred while processing your request. Please try again."
            }
            return JsonResponse(data, status=500)
    else:
        return render(request, "forgot_password.html", {})




def set_password(request, user_id, passwd_reset_token):
    """
    Handles password reset functionality.
    GET: Display the set password page
    POST: Process password reset via AJAX and return JSON response
    """
    user = User.objects.filter(id=user_id, password_reset_token=passwd_reset_token).first()

    # Return 404 if user not found
    if not user:
        template = "404.html"
        return render(
            request,
            template,
            {"message": "Not Found", "reason": "URL may have expired"},
            status=404,
        )
    
    # Check if token has expired (add token expiry validation)
    from datetime import timedelta
    if user.password_reset_token_created_at:
        token_age = timezone.now() - user.password_reset_token_created_at
        if token_age > timedelta(hours=24):  # Token expires after 24 hours
            template = "404.html"
            return render(
                request,
                template,
                {"message": "Reset Link Expired", "reason": "Please request a new password reset link"},
                status=410,
            )
    
    if request.method == "POST":
        try:
            validate_changepassword = UserPassChangeForm(request.POST)
            
            if validate_changepassword.is_valid():
                new_password = request.POST.get("new_password")
                retype_password = request.POST.get("retype_password")
                
                # Check if passwords match
                if new_password != retype_password:
                    data = {
                        "error": True,
                        "message": "Password and Confirm Password do not match",
                    }
                    return JsonResponse(data)
                
                # Check password length (updated to match form validation)
                if len(new_password) < 8:
                    data = {
                        "error": True,
                        "message": "Password must be at least 8 characters long",
                    }
                    return JsonResponse(data)
                
                # Update user password
                user.set_password(new_password)
                user.password_reset_token = None
                user.password_reset_token_created_at = None  # Clear the timestamp too
                user.save()
                
                # Authenticate and login user
                usr = authenticate(username=user.email, password=new_password)
                if usr:
                    usr.last_login = timezone.now()
                    usr.save()
                    auth_login(request, usr)
                
                # Determine redirect URL based on user type
                if user.user_type in ["RR", "RA", "AA", "AR"]:
                    url = reverse("recruiter:dashboard")
                else:
                    url = "/"
                
                data = {
                    "error": False,
                    "message": "Password changed successfully! Redirecting...",
                    "url": url,
                }
                return JsonResponse(data)
            else:
                # Form validation errors
                error_messages = []
                for field, errors in validate_changepassword.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                data = {
                    "error": True,
                    "message": "Please correct the following errors: " + "; ".join(error_messages)
                }
                return JsonResponse(data)
                
        except Exception as e:
            logger.error(f"Exception during password reset: {str(e)}", exc_info=True)
            data = {
                "error": True,
                "message": "An error occurred while setting password. Please try again."
            }
            return JsonResponse(data, status=500)
    
    # For GET requests, show the set password page
    return render(request, "set_password.html", {"user_id": user_id})
