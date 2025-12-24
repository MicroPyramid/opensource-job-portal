import json
import random
import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from datetime import datetime

from mpcomp.views import jobseeker_login_required
from mpcomp.views import get_resume_data, handle_uploaded_file
from peeldb.models import City, Country, FunctionalArea, Industry, Language, Skill, UserMessage, Project, UserLanguage, EmploymentHistory, EducationDetails, EducationInstitue, Degree, Qualification, TechnicalSkill, Certification

from candidate.forms import (
    YEARS,
    MONTHS,
    MAR_TYPES,
    ProjectForm,
    WorkExperienceForm,
    EducationForm,
    DegreeForm,
    EducationInstitueForm,
    TechnicalSkillForm,
    CertificationForm,
)

@jobseeker_login_required
def my_home(request):
    """need to check user login or not"""
    messages = UserMessage.objects.filter(message_to=request.user.id, is_read=False)
    user = request.user
    user.profile_completeness = user.profile_completion_percentage
    user.save()

    nationality = ""
    functional_areas = FunctionalArea.objects.filter(status="Active").order_by(
        "name"
    )
    cities = (
        City.objects.filter(status="Enabled")
        .exclude(slug__icontains="india")
        .order_by("name")
    )
    skills = Skill.objects.filter(status="Active").order_by("name")
    industries = (
        Industry.objects.filter(status="Active").order_by("name").exclude(id=36)
    )
    if request.user.nationality:
        try:
            nationality = Country.objects.get(id=request.user.nationality)
        except (Country.DoesNotExist, ValueError):
            # If nationality is stored as text, not an ID
            nationality = None
    
    # Get user's education details
    user_education = user.education.all()
    
    # Get user's employment history
    user_employment = user.employment_history.all().order_by('-id')
    
    # Get user's projects
    user_projects = user.project.all()
    
    # Get user's languages
    user_languages = user.language.all()
    
    # Get user's certifications
    user_certifications = Certification.objects.filter(user=user).order_by('-issued_date', '-created_at')
    
    # Get qualifications for education form
    qualifications = Qualification.objects.filter(status="Active").order_by("name")
    
    # Prepare cities as JSON for the basic profile edit modal
    cities_json = json.dumps([
        {
            'id': city.id,
            'name': city.name,
            'state': city.state.name if city.state else ''
        }
        for city in cities
    ])
    
    return render(
        request,
        "my/home.html",
        {
            "nationality": nationality,
            "cities": cities,
            "cities_json": cities_json,
            "skills": skills,
            "years": YEARS,
            "months": MONTHS,
            "industries": industries,
            "languages": Language.objects.all(),
            "martial_status": MAR_TYPES,
            "functional_areas": functional_areas,
            "unread_messages": messages.count(),
            "user_education": user_education,
            "qualifications": qualifications,
            "user_employment": user_employment,
            "user_projects": user_projects,
            "user_languages": user_languages,
            "user_certifications": user_certifications,
        },
    )

@jobseeker_login_required
@require_http_methods(["POST"])
def edit_profile_description(request):
    """AJAX view to update profile description"""
    try:
        data = json.loads(request.body)
        description = data.get('description', '').strip()
        
        # Validate description length (optional)
        if len(description) > 5000:
            return JsonResponse({
                'success': False,
                'error': 'Description is too long. Maximum 5000 characters allowed.'
            })
        
        # Update user profile description
        request.user.profile_description = description
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile description updated successfully!',
            'description': description
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid data format.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while updating your profile description.'
        })

@jobseeker_login_required
@require_http_methods(["POST"])
def edit_personal_info(request):
    """AJAX view to update personal information"""
    try:
        data = json.loads(request.body)
        user = request.user
        
        with transaction.atomic():
            # Update basic information
            user.first_name = data.get('first_name', '').strip()
            user.last_name = data.get('last_name', '').strip() or None
            
            # Mobile validation
            mobile = data.get('mobile', '').strip()
            if mobile:
                # Check if mobile is already used by another user
                from peeldb.models import User
                existing_user = User.objects.filter(mobile=mobile).exclude(id=user.id).first()
                if existing_user:
                    return JsonResponse({
                        'success': False,
                        'error': 'This mobile number is already registered with another account.'
                    })
                user.mobile = mobile
            
            # Update other contact info
            alternate_mobile = data.get('alternate_mobile', '').strip()
            if alternate_mobile:
                try:
                    user.alternate_mobile = int(alternate_mobile)
                except ValueError:
                    user.alternate_mobile = None
            else:
                user.alternate_mobile = None
            
            # Date of birth
            dob = data.get('dob', '').strip()
            if dob:
                try:
                    user.dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid date format for date of birth.'
                    })
            else:
                user.dob = None
            
            # Gender and marital status
            user.gender = data.get('gender', '') or None
            user.marital_status = data.get('marital_status', '') or None
            
            # Nationality
            user.nationality = data.get('nationality', '').strip() or None
            
            # Salary information
            user.current_salary = data.get('current_salary', '').strip() or None
            user.expected_salary = data.get('expected_salary', '').strip() or None
            
            # Notice period
            user.notice_period = data.get('notice_period', '') or None
            
            # Address information
            user.address = data.get('address', '').strip() or None
            user.permanent_address = data.get('permanent_address', '').strip() or None
            
            # Pincode
            pincode = data.get('pincode', '').strip()
            if pincode:
                try:
                    user.pincode = int(pincode)
                except ValueError:
                    user.pincode = None
            else:
                user.pincode = None
            
            # Update profile updated timestamp
            user.profile_updated = timezone.now()
            
            # Save user
            user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Personal information updated successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid data format.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while updating your personal information.'
        })

@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def edit_project_modal(request, project_id):
    """Edit project via modal form"""
    try:
        project = request.user.project.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Project not found'
        }, status=404)
    
    if request.method == 'GET':
        # Return project data for modal form
        project_data = {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'from_date': project.from_date.strftime('%Y-%m-%d') if project.from_date else '',
            'to_date': project.to_date.strftime('%Y-%m-%d') if project.to_date else '',
            'role': project.role or '',
            'size': project.size or '',
            'location': project.location.id if project.location else '',
            'skills': [skill.id for skill in project.skills.all()],
        }
        
        # Get skills and cities for the form
        skills_data = [{'id': skill.id, 'name': skill.name} for skill in Skill.objects.filter(status='Active').order_by('name')]
        cities_data = [{'id': city.id, 'name': city.name} for city in City.objects.filter(status='Enabled').order_by('name')]
        
        return JsonResponse({
            'success': True,
            'data': {
                'project': project_data,
                'skills': skills_data,
                'cities': cities_data,
            }
        })
    
    elif request.method == 'POST':
        # Process form submission
        form = ProjectForm(request.POST, instance=project)
        
        if form.is_valid():
            # Check for duplicate project names (excluding current project)
            if request.user.project.filter(
                name=request.POST.get('name')
            ).exclude(id=project_id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Project with this name already exists'
                })
            
            # Save the project
            project = form.save()
            
            # Update additional fields
            if request.POST.get('role'):
                project.role = request.POST.get('role')
            if request.POST.get('size'):
                project.size = request.POST.get('size')
            if request.POST.get('location'):
                try:
                    project.location = City.objects.get(id=request.POST.get('location'))
                except City.DoesNotExist:
                    pass
            
            project.save()
            
            # Update user's profile timestamp
            request.user.profile_updated = timezone.now()
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Project updated successfully',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'from_date': project.from_date.strftime('%B %Y') if project.from_date else '',
                    'to_date': project.to_date.strftime('%B %Y') if project.to_date else 'Present',
                    'role': project.role or '',
                    'size': project.size or '',
                    'location': project.location.name if project.location else '',
                    'skills': [{'id': skill.id, 'name': skill.name} for skill in project.skills.all()],
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below',
                'errors': form.errors
            })

@jobseeker_login_required
@require_http_methods(["POST"])
def delete_project_modal(request, project_id):
    """Delete project via AJAX"""
    try:
        project = request.user.project.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Project not found'
        }, status=404)
    
    # Remove project from user's projects and delete it
    request.user.project.remove(project)
    project.delete()
    
    # Update user's profile timestamp
    request.user.profile_updated = timezone.now()
    request.user.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Project deleted successfully'
    })

@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def add_project_modal(request):
    """Add new project via modal form"""
    
    if request.method == 'GET':
        # Return form data for modal
        skills_data = [{'id': skill.id, 'name': skill.name} for skill in Skill.objects.filter(status='Active').order_by('name')]
        cities_data = [{'id': city.id, 'name': city.name} for city in City.objects.filter(status='Enabled').order_by('name')]
        
        return JsonResponse({
            'success': True,
            'data': {
                'skills': skills_data,
                'cities': cities_data,
            }
        })
    
    elif request.method == 'POST':
        # Process form submission
        form = ProjectForm(request.POST)
        
        if form.is_valid():
            # Check for duplicate project names
            if request.user.project.filter(name=request.POST.get('name')).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Project with this name already exists'
                })
            
            # Save the project
            project = form.save()
            
            # Update additional fields
            if request.POST.get('role'):
                project.role = request.POST.get('role')
            if request.POST.get('size'):
                project.size = request.POST.get('size')
            if request.POST.get('location'):
                try:
                    project.location = City.objects.get(id=request.POST.get('location'))
                except City.DoesNotExist:
                    pass
            
            project.save()
            
            # Add project to user
            request.user.project.add(project)
            
            # Update user's profile timestamp
            request.user.profile_updated = timezone.now()
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Project added successfully',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'from_date': project.from_date.strftime('%B %Y') if project.from_date else '',
                    'to_date': project.to_date.strftime('%B %Y') if project.to_date else 'Present',
                    'role': project.role or '',
                    'size': project.size or '',
                    'location': project.location.name if project.location else '',
                    'skills': [{'id': skill.id, 'name': skill.name} for skill in project.skills.all()],
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below',
                'errors': form.errors
            })

@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def edit_language_modal(request, language_id):
    """AJAX view to edit language in modal"""
    try:
        user_language = get_object_or_404(UserLanguage, id=language_id)
        
        # Check if the language belongs to the current user
        if user_language not in request.user.language.all():
            return JsonResponse({
                'success': False,
                'error': 'Language not found or access denied'
            })
        
        if request.method == 'GET':
            # Return language data for editing
            return JsonResponse({
                'success': True,
                'language': {
                    'id': user_language.id,
                    'language_id': user_language.language.id,
                    'language_name': user_language.language.name,
                    'read': user_language.read,
                    'write': user_language.write,
                    'speak': user_language.speak,
                }
            })
        
        elif request.method == 'POST':
            # Update language
            language_id = request.POST.get('language')
            read = request.POST.get('read') == '1'
            write = request.POST.get('write') == '1'
            speak = request.POST.get('speak') == '1'
            
            # Validation
            errors = {}
            
            if not language_id:
                errors['language'] = 'Please select a language'
            
            if not (read or write or speak):
                errors['proficiency'] = 'Please select at least one proficiency level'
            
            if errors:
                return JsonResponse({
                    'success': False,
                    'errors': errors
                })
            
            # Check if user already has this language (if different from current)
            language_obj = get_object_or_404(Language, id=language_id)
            if language_obj != user_language.language:
                existing_language = request.user.language.filter(language=language_obj).first()
                if existing_language:
                    return JsonResponse({
                        'success': False,
                        'errors': {'language': 'You already have this language in your profile'}
                    })
            
            # Update the language
            with transaction.atomic():
                user_language.language = language_obj
                user_language.read = read
                user_language.write = write
                user_language.speak = speak
                user_language.save()
                
                # Update user's profile timestamp
                request.user.profile_updated = timezone.now()
                request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Language updated successfully'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@jobseeker_login_required
@require_http_methods(["POST"])
def add_language_modal(request):
    """AJAX view to add language in modal"""
    try:
        language_id = request.POST.get('language')
        read = request.POST.get('read') == '1'
        write = request.POST.get('write') == '1'
        speak = request.POST.get('speak') == '1'
        
        # Validation
        errors = {}
        
        if not language_id:
            errors['language'] = 'Please select a language'
        
        if not (read or write or speak):
            errors['proficiency'] = 'Please select at least one proficiency level'
        
        if errors:
            return JsonResponse({
                'success': False,
                'errors': errors
            })
        
        # Check if user already has this language
        language_obj = get_object_or_404(Language, id=language_id)
        existing_language = request.user.language.filter(language=language_obj).first()
        if existing_language:
            return JsonResponse({
                'success': False,
                'errors': {'language': 'You already have this language in your profile'}
            })
        
        # Create new language
        with transaction.atomic():
            user_language = UserLanguage.objects.create(
                language=language_obj,
                read=read,
                write=write,
                speak=speak
            )
            
            # Add to user's languages
            request.user.language.add(user_language)
            
            # Update user's profile timestamp
            request.user.profile_updated = timezone.now()
            request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Language added successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@jobseeker_login_required
@require_http_methods(["POST"])
def delete_language_modal(request, language_id):
    """AJAX view to delete language"""
    try:
        user_language = get_object_or_404(UserLanguage, id=language_id)
        
        # Check if the language belongs to the current user
        if user_language not in request.user.language.all():
            return JsonResponse({
                'success': False,
                'error': 'Language not found or access denied'
            })
        
        with transaction.atomic():
            # Remove from user's languages
            request.user.language.remove(user_language)
            
            # Delete the language
            user_language.delete()
            
            # Update user's profile timestamp
            request.user.profile_updated = timezone.now()
            request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Language deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def edit_experience_modal(request, experience_id):
    """Edit experience via modal form"""
    try:
        experience = get_object_or_404(EmploymentHistory, id=experience_id)
        
        # Check if the experience belongs to the current user
        if not request.user.employment_history.filter(id=experience_id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Experience not found or access denied'
            }, status=404)
        
        if request.method == 'GET':
            # Return experience data for modal form
            experience_data = {
                'id': experience.id,
                'designation': experience.designation,
                'company': experience.company,
                'from_date': experience.from_date.strftime('%Y-%m-%d') if experience.from_date else '',
                'to_date': experience.to_date.strftime('%Y-%m-%d') if experience.to_date else '',
                'current_job': experience.current_job,
                'job_profile': experience.job_profile or '',
            }
            return JsonResponse({
                'success': True,
                'data': {
                    'experience': experience_data
                }
            })
        elif request.method == 'POST':
            data = json.loads(request.body)
            errors = {}
            if not data.get('designation', '').strip():
                errors['designation'] = 'Job title is required.'
            if not data.get('company', '').strip():
                errors['company'] = 'Company name is required.'
            if not data.get('from_date', '').strip():
                errors['from_date'] = 'Start date is required.'
            # Validate dates
            from_date = None
            to_date = None
            try:
                from_date = datetime.strptime(data.get('from_date'), '%Y-%m-%d')
            except (ValueError, TypeError):
                errors['from_date'] = 'Invalid start date.'
            if data.get('to_date') and not data.get('current_job', False):
                try:
                    to_date = datetime.strptime(data.get('to_date'), '%Y-%m-%d')
                except (ValueError, TypeError):
                    errors['to_date'] = 'Invalid end date.'
            # Check for duplicate experiences (same company and designation, excluding current)
            duplicate_check = request.user.employment_history.filter(
                company=data.get('company', '').strip(),
                designation=data.get('designation', '').strip()
            ).exclude(id=experience_id)
            if duplicate_check.exists():
                errors['duplicate'] = 'You have already added this experience.'
            if errors:
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below',
                    'errors': errors
                })
            # Update experience
            with transaction.atomic():
                experience.designation = data.get('designation', '').strip()
                experience.company = data.get('company', '').strip()
                experience.from_date = from_date
                experience.to_date = to_date if not data.get('current_job', False) else None
                experience.current_job = data.get('current_job', False)
                experience.job_profile = data.get('job_profile', '').strip() or None
                experience.save()
                request.user.profile_updated = timezone.now()
                request.user.save()
            return JsonResponse({
                'success': True,
                'message': 'Experience updated successfully'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@jobseeker_login_required
@require_http_methods(["POST"])
def add_experience_modal(request):
    """Add new experience via modal form"""
    try:
        data = json.loads(request.body)
        errors = {}
        if not data.get('designation', '').strip():
            errors['designation'] = 'Job title is required.'
        if not data.get('company', '').strip():
            errors['company'] = 'Company name is required.'
        if not data.get('from_date', '').strip():
            errors['from_date'] = 'Start date is required.'
        # Validate dates
        from_date = None
        to_date = None
        try:
            from_date = datetime.strptime(data.get('from_date'), '%Y-%m-%d')
        except (ValueError, TypeError):
            errors['from_date'] = 'Invalid start date.'
        if data.get('to_date') and not data.get('current_job', False):
            try:
                to_date = datetime.strptime(data.get('to_date'), '%Y-%m-%d')
            except (ValueError, TypeError):
                errors['to_date'] = 'Invalid end date.'
        # Check for duplicate experiences (same company and designation)
        duplicate_check = request.user.employment_history.filter(
            company=data.get('company', '').strip(),
            designation=data.get('designation', '').strip()
        )
        if duplicate_check.exists():
            errors['duplicate'] = 'You have already added this experience.'
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below',
                'errors': errors
            })
        # Create new experience
        with transaction.atomic():
            new_exp = EmploymentHistory.objects.create(
                user=request.user,
                designation=data.get('designation', '').strip(),
                company=data.get('company', '').strip(),
                from_date=from_date,
                to_date=to_date if not data.get('current_job', False) else None,
                current_job=data.get('current_job', False),
                job_profile=data.get('job_profile', '').strip() or None,
            )
            request.user.profile_updated = timezone.now()
            request.user.save()
        return JsonResponse({
            'success': True,
            'message': 'Experience added successfully'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid data format'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@jobseeker_login_required
@require_http_methods(["POST"])
def delete_experience_modal(request, experience_id):
    """Delete experience via AJAX"""
    try:
        experience = get_object_or_404(EmploymentHistory, id=experience_id)
        
        # Check if the experience belongs to the current user
        if not request.user.employment_history.filter(id=experience_id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Experience not found or access denied'
            }, status=404)
        
        with transaction.atomic():
            # Remove experience from user's employment history and delete it
            request.user.employment_history.remove(experience)
            experience.delete()
            
            # Update user's profile timestamp
            request.user.profile_updated = timezone.now()
            request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Experience deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@jobseeker_login_required
@require_http_methods(["GET"])
def test_experience_view(request):
    """Simple test view to check if user has experiences"""
    experiences = request.user.employment_history.all()
    return JsonResponse({
        'success': True,
        'count': experiences.count(),
        'experiences': [
            {
                'id': exp.id,
                'company': exp.company,
                'designation': exp.designation,
                'from_date': exp.from_date.strftime('%Y-%m-%d') if exp.from_date else None,
                'to_date': exp.to_date.strftime('%Y-%m-%d') if exp.to_date else None,
                'current_job': exp.current_job,
            }
            for exp in experiences
        ]
    })

@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def edit_education_modal(request, education_id):
    """Edit education via modal form"""
    try:
        education = request.user.education.get(id=education_id)
    except EducationDetails.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Education not found'
        }, status=404)
    
    if request.method == 'GET':
        # Return education data for modal form
        education_data = {
            'id': education.id,
            'institute_name': education.institute.name,
            'institute_city': education.institute.city.id if education.institute.city else '',
            'degree_name': education.degree.degree_name.id if education.degree.degree_name else '',
            'degree_type': education.degree.degree_type,
            'specialization': education.degree.specialization,
            'from_date': education.from_date.strftime('%Y-%m-%d') if education.from_date else '',
            'to_date': education.to_date.strftime('%Y-%m-%d') if education.to_date else '',
            'current_education': education.current_education,
            'score': education.score,
        }
        
        return JsonResponse({
            'success': True,
            'data': {
                'education': education_data,
            }
        })
    
    elif request.method == 'POST':
        # Process form submission
        try:
            with transaction.atomic():
                # Update or create institute
                institute_name = request.POST.get('institute_name', '').strip()
                institute_city_id = request.POST.get('institute_city')
                
                if not institute_name or not institute_city_id:
                    return JsonResponse({
                        'success': False,
                        'error': 'Institution name and city are required'
                    })
                
                try:
                    institute_city = City.objects.get(id=institute_city_id)
                except City.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid city selected'
                    })
                
                # Update institute or create new one if name changed
                if education.institute.name != institute_name or education.institute.city != institute_city:
                    institute, created = EducationInstitue.objects.get_or_create(
                        name=institute_name,
                        city=institute_city,
                        defaults={'address': ''}
                    )
                    education.institute = institute
                
                # Update or create degree
                degree_name_id = request.POST.get('degree_name')
                degree_type = request.POST.get('degree_type')
                specialization = request.POST.get('specialization', '').strip()
                
                if not degree_name_id or not degree_type or not specialization:
                    return JsonResponse({
                        'success': False,
                        'error': 'Degree, type, and specialization are required'
                    })
                
                try:
                    degree_name = Qualification.objects.get(id=degree_name_id)
                except Qualification.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid degree selected'
                    })
                
                # Update degree or create new one if details changed
                if (education.degree.degree_name != degree_name or 
                    education.degree.degree_type != degree_type or 
                    education.degree.specialization != specialization):
                    
                    degree, created = Degree.objects.get_or_create(
                        degree_name=degree_name,
                        degree_type=degree_type,
                        specialization=specialization
                    )
                    education.degree = degree
                
                # Update education details
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                current_education = request.POST.get('current_education') == '1'
                score = request.POST.get('score', '').strip()
                
                if not from_date:
                    return JsonResponse({
                        'success': False,
                        'error': 'From date is required'
                    })
                
                try:
                    education.from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                    if to_date and not current_education:
                        education.to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                        if education.to_date < education.from_date:
                            return JsonResponse({
                                'success': False,
                                'error': 'To date cannot be earlier than from date'
                            })
                    else:
                        education.to_date = None
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid date format'
                    })
                
                education.current_education = current_education
                education.score = score
                
                education.save()
                
                # Update user's profile timestamp
                request.user.profile_updated = timezone.now()
                request.user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Education updated successfully'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@jobseeker_login_required
@require_http_methods(["POST"])
def add_education_modal(request):
    """Add new education via modal form"""
    try:
        with transaction.atomic():
            # Create or get institute
            institute_name = request.POST.get('institute_name', '').strip()
            institute_city_id = request.POST.get('institute_city')
            
            if not institute_name or not institute_city_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Institution name and city are required'
                })
            
            try:
                institute_city = City.objects.get(id=institute_city_id)
            except City.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid city selected'
                })
            
            institute, created = EducationInstitue.objects.get_or_create(
                name=institute_name,
                city=institute_city,
                defaults={'address': ''}
            )
            
            # Create or get degree
            degree_name_id = request.POST.get('degree_name')
            degree_type = request.POST.get('degree_type')
            specialization = request.POST.get('specialization', '').strip()
            
            if not degree_name_id or not degree_type or not specialization:
                return JsonResponse({
                    'success': False,
                    'error': 'Degree, type, and specialization are required'
                })
            
            try:
                degree_name = Qualification.objects.get(id=degree_name_id)
            except Qualification.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid degree selected'
                })
            
            degree, created = Degree.objects.get_or_create(
                degree_name=degree_name,
                degree_type=degree_type,
                specialization=specialization
            )
            
            # Create education details
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            current_education = request.POST.get('current_education') == '1'
            score = request.POST.get('score', '').strip()
            
            if not from_date:
                return JsonResponse({
                    'success': False,
                    'error': 'From date is required'
                })
            
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date_obj = None
                if to_date and not current_education:
                    to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
                    if to_date_obj < from_date_obj:
                        return JsonResponse({
                            'success': False,
                            'error': 'To date cannot be earlier than from date'
                        })
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid date format'
                })
            
            education = EducationDetails.objects.create(
                institute=institute,
                degree=degree,
                from_date=from_date_obj,
                to_date=to_date_obj,
                current_education=current_education,
                score=score
            )
            
            # Add to user's education
            request.user.education.add(education)
            
            # Update user's profile timestamp
            request.user.profile_updated = timezone.now()
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Education added successfully'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@jobseeker_login_required
@require_http_methods(["POST"])
def delete_education_modal(request, education_id):
    """Delete education via AJAX"""
    try:
        education = request.user.education.get(id=education_id)
    except EducationDetails.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Education not found'
        }, status=404)
    
    with transaction.atomic():
        # Remove education from user's education and delete it
        request.user.education.remove(education)
        education.delete()
        
        # Update user's profile timestamp
        request.user.profile_updated = timezone.now()
        request.user.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Education deleted successfully'
    })

# Technical Skills Management Functions

@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def add_skill_modal(request):
    """Add new technical skill via modal form"""
    
    if request.method == 'GET':
        # Return form data for modal
        skills_data = [{'id': skill.id, 'name': skill.name} for skill in Skill.objects.filter(status='Active').order_by('name')]
        
        return JsonResponse({
            'success': True,
            'data': {
                'skills': skills_data,
                'years': YEARS,
                'months': MONTHS,
            }
        })
    
    elif request.method == 'POST':
        # Process form submission
        try:
            skill_id = request.POST.get('skill')
            proficiency = request.POST.get('proficiency')
            year = request.POST.get('year')
            month = request.POST.get('month')
            version = request.POST.get('version', '')
            last_used = request.POST.get('last_used')
            is_major = request.POST.get('is_major') == '1'
            
            # Validate required fields
            if not skill_id or not year or not month:
                return JsonResponse({
                    'success': False,
                    'message': 'Please fill in all required fields.'
                })
            
            # Get the skill object
            try:
                skill = Skill.objects.get(id=skill_id)
            except Skill.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Selected skill does not exist.'
                })
            
            # Check if user already has this skill
            if request.user.skills.filter(skill=skill).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'You already have this skill in your profile.'
                })
            
            # Check major skills limit
            if is_major and request.user.skills.filter(is_major=True).count() >= 2:
                return JsonResponse({
                    'success': False,
                    'message': 'You can only have maximum 2 major skills.'
                })
            
            # Create new technical skill
            with transaction.atomic():
                technical_skill = TechnicalSkill.objects.create(
                    skill=skill,
                    year=int(year),
                    month=int(month),
                    proficiency=proficiency if proficiency else None,
                    version=version if version else None,
                    is_major=is_major
                )
                
                # Parse last_used date if provided
                if last_used:
                    try:
                        technical_skill.last_used = datetime.strptime(last_used, '%Y-%m-%d').date()
                        technical_skill.save()
                    except ValueError:
                        pass  # Invalid date format, skip it
                
                # Add to user's skills
                request.user.skills.add(technical_skill)
                
                # Update user's profile timestamp
                request.user.profile_updated = timezone.now()
                request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Technical skill added successfully!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while adding the skill.'
            })


@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def edit_skill_modal(request, skill_id):
    """Edit technical skill via modal form"""
    try:
        technical_skill = get_object_or_404(TechnicalSkill, id=skill_id)
        
        # Check if the skill belongs to the current user
        if technical_skill not in request.user.skills.all():
            return JsonResponse({
                'success': False,
                'message': 'Skill not found or access denied.'
            }, status=404)
        
        if request.method == 'GET':
            # Return skill data for modal form
            skill_data = {
                'id': technical_skill.id,
                'skill_id': technical_skill.skill.id,
                'skill_name': technical_skill.skill.name,
                'proficiency': technical_skill.proficiency or '',
                'year': technical_skill.year or 0,
                'month': technical_skill.month or 0,
                'version': technical_skill.version or '',
                'last_used': technical_skill.last_used.strftime('%Y-%m-%d') if technical_skill.last_used else '',
                'is_major': technical_skill.is_major,
            }
            
            # Get skills and other data for the form
            skills_data = [{'id': skill.id, 'name': skill.name} for skill in Skill.objects.filter(status='Active').order_by('name')]
            
            return JsonResponse({
                'success': True,
                'data': {
                    'skill': skill_data,
                    'skills': skills_data,
                    'years': YEARS,
                    'months': MONTHS,
                }
            })
        
        elif request.method == 'POST':
            # Process form submission
            try:
                skill_id_new = request.POST.get('skill')
                proficiency = request.POST.get('proficiency')
                year = request.POST.get('year')
                month = request.POST.get('month')
                version = request.POST.get('version', '')
                last_used = request.POST.get('last_used')
                is_major = request.POST.get('is_major') == '1'
                
                # Validate required fields
                if not skill_id_new or not year or not month:
                    return JsonResponse({
                        'success': False,
                        'message': 'Please fill in all required fields.'
                    })
                
                # Get the skill object
                try:
                    skill = Skill.objects.get(id=skill_id_new)
                except Skill.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Selected skill does not exist.'
                    })
                
                # Check if user already has this skill (excluding current one)
                if request.user.skills.filter(skill=skill).exclude(id=technical_skill.id).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'You already have this skill in your profile.'
                    })
                
                # Check major skills limit (excluding current one if it was major)
                current_major_count = request.user.skills.filter(is_major=True).count()
                if technical_skill.is_major:
                    current_major_count -= 1  # Subtract current skill if it was major
                
                if is_major and current_major_count >= 2:
                    return JsonResponse({
                        'success': False,
                        'message': 'You can only have maximum 2 major skills.'
                    })
                
                # Update technical skill
                with transaction.atomic():
                    technical_skill.skill = skill
                    technical_skill.year = int(year)
                    technical_skill.month = int(month)
                    technical_skill.proficiency = proficiency if proficiency else None
                    technical_skill.version = version if version else None
                    technical_skill.is_major = is_major
                    
                    # Parse last_used date if provided
                    if last_used:
                        try:
                            technical_skill.last_used = datetime.strptime(last_used, '%Y-%m-%d').date()
                        except ValueError:
                            technical_skill.last_used = None
                    else:
                        technical_skill.last_used = None
                    
                    technical_skill.save()
                    
                    # Update user's profile timestamp
                    request.user.profile_updated = timezone.now()
                    request.user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Technical skill updated successfully!'
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': 'An error occurred while updating the skill.'
                })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while processing your request.'
        })


@jobseeker_login_required
@require_http_methods(["POST"])
def delete_skill_modal(request, skill_id):
    """Delete technical skill via AJAX"""
    try:
        technical_skill = get_object_or_404(TechnicalSkill, id=skill_id)
        
        # Check if the skill belongs to the current user
        if technical_skill not in request.user.skills.all():
            return JsonResponse({
                'success': False,
                'message': 'Skill not found or access denied.'
            }, status=404)
        
        with transaction.atomic():
            # Remove skill from user's skills and delete it
            request.user.skills.remove(technical_skill)
            technical_skill.delete()
            
            # Update user's profile timestamp
            request.user.profile_updated = timezone.now()
            request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Technical skill deleted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while deleting the skill.'
        })

@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def edit_job_preferences(request):
    """AJAX view to edit job preferences"""
    
    if request.method == 'GET':
        # Return job preferences data for modal form
        try:
            # Get all available data
            cities_data = [
                {'id': city.id, 'name': city.name} 
                for city in City.objects.filter(status='Enabled').order_by('name')
            ]
            functional_areas_data = [
                {'id': area.id, 'name': area.name} 
                for area in FunctionalArea.objects.filter(status='Active').order_by('name')
            ]
            industries_data = [
                {'id': industry.id, 'name': industry.name} 
                for industry in Industry.objects.filter(status='Active').order_by('name')
            ]
            
            # Get user's selected preferences
            selected_cities = [
                {'id': city.id, 'name': city.name} 
                for city in request.user.preferred_city.all()
            ]
            selected_functional_areas = [
                {'id': area.id, 'name': area.name} 
                for area in request.user.functional_area.all()
            ]
            selected_industries = [
                {'id': industry.id, 'name': industry.name} 
                for industry in request.user.industry.all()
            ]
            
            return JsonResponse({
                'success': True,
                'data': {
                    'cities': cities_data,
                    'functional_areas': functional_areas_data,
                    'industries': industries_data,
                    'selected_cities': selected_cities,
                    'selected_functional_areas': selected_functional_areas,
                    'selected_industries': selected_industries,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to load job preferences data.'
            })
    
    elif request.method == 'POST':
        # Process job preferences update
        try:
            data = json.loads(request.body)
            user = request.user
            
            with transaction.atomic():
                # Update preferred cities
                city_ids = data.get('cities', [])
                if city_ids:
                    cities = City.objects.filter(id__in=city_ids, status='Enabled')
                    user.preferred_city.set(cities)
                else:
                    user.preferred_city.clear()
                
                # Update functional areas
                functional_area_ids = data.get('functional_areas', [])
                if functional_area_ids:
                    functional_areas = FunctionalArea.objects.filter(
                        id__in=functional_area_ids, 
                        status='Active'
                    )
                    user.functional_area.set(functional_areas)
                else:
                    user.functional_area.clear()
                
                # Update industries
                industry_ids = data.get('industries', [])
                if industry_ids:
                    industries = Industry.objects.filter(
                        id__in=industry_ids, 
                        status='Active'
                    )
                    user.industry.set(industries)
                else:
                    user.industry.clear()
                
                # Update profile timestamp
                user.profile_updated = timezone.now()
                user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Job preferences updated successfully!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid data format.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while updating job preferences.'
            })

@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def edit_account_settings(request):
    """AJAX view to edit account settings"""
    
    if request.method == 'GET':
        # Return current account settings data for modal form
        user = request.user
        account_data = {
            'email_notifications': user.email_notifications,
            'show_email': user.show_email,
            'is_looking_for_job': user.is_looking_for_job,
            'is_open_to_offers': user.is_open_to_offers,
            'relocation': user.relocation,
            'is_unsubscribe': user.is_unsubscribe,
        }
        
        return JsonResponse({
            'success': True,
            'data': account_data
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            
            with transaction.atomic():
                # Update notification settings
                user.email_notifications = data.get('email_notifications', False)
                user.show_email = data.get('show_email', False)
                
                # Update job preferences
                user.is_looking_for_job = data.get('is_looking_for_job', False)
                user.is_open_to_offers = data.get('is_open_to_offers', False)
                user.relocation = data.get('relocation', False)
                
                # Update subscription settings
                user.is_unsubscribe = data.get('is_unsubscribe', False)
                
                # Update profile timestamp
                user.profile_updated = timezone.now()
                user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Account settings updated successfully!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid data format.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while updating account settings.'
            })


# Certification Management Functions

@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def add_certification_modal(request):
    """Add new certification via modal form"""
    
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'data': {
                'form_html': 'certification_form_html'  # This will be handled by frontend
            }
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create certification instance
            certification = Certification()
            certification.user = request.user
            certification.name = data.get('name', '').strip()
            certification.organization = data.get('organization', '').strip()
            certification.credential_id = data.get('credential_id', '').strip()
            certification.credential_url = data.get('credential_url', '').strip()
            certification.description = data.get('description', '').strip()
            certification.does_not_expire = data.get('does_not_expire', False)
            
            # Handle dates
            issued_date = data.get('issued_date')
            if issued_date:
                certification.issued_date = datetime.strptime(issued_date, '%Y-%m-%d').date()
                
            expiry_date = data.get('expiry_date')
            if expiry_date and not certification.does_not_expire:
                certification.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            
            # Validation
            if not certification.name or not certification.organization:
                return JsonResponse({
                    'success': False,
                    'error': 'Certification name and organization are required.'
                })
            
            if certification.issued_date and certification.expiry_date:
                if certification.issued_date > certification.expiry_date:
                    return JsonResponse({
                        'success': False,
                        'error': 'Issue date cannot be later than expiry date.'
                    })
            
            if not certification.does_not_expire and not certification.expiry_date:
                return JsonResponse({
                    'success': False,
                    'error': 'Please provide an expiry date or check "This certification does not expire".'
                })
            
            with transaction.atomic():
                certification.save()
                request.user.profile_updated = timezone.now()
                request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Certification added successfully!',
                'certification': {
                    'id': certification.id,
                    'name': certification.name,
                    'organization': certification.organization,
                    'credential_id': certification.credential_id,
                    'credential_url': certification.credential_url,
                    'issued_date': certification.issued_date.strftime('%Y-%m-%d') if certification.issued_date else '',
                    'expiry_date': certification.expiry_date.strftime('%Y-%m-%d') if certification.expiry_date else '',
                    'does_not_expire': certification.does_not_expire,
                    'description': certification.description,
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid data format.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while adding the certification.'
            })


@jobseeker_login_required
@require_http_methods(["GET", "POST"])
def edit_certification_modal(request, certification_id):
    """Edit certification via modal form"""
    try:
        certification = Certification.objects.get(id=certification_id, user=request.user)
    except Certification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Certification not found'
        }, status=404)
    
    if request.method == 'GET':
        # Return certification data for modal form
        certification_data = {
            'id': certification.id,
            'name': certification.name,
            'organization': certification.organization,
            'credential_id': certification.credential_id or '',
            'credential_url': certification.credential_url or '',
            'issued_date': certification.issued_date.strftime('%Y-%m-%d') if certification.issued_date else '',
            'expiry_date': certification.expiry_date.strftime('%Y-%m-%d') if certification.expiry_date else '',
            'does_not_expire': certification.does_not_expire,
            'description': certification.description or '',
        }
        
        return JsonResponse({
            'success': True,
            'data': {
                'certification': certification_data,
            }
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            with transaction.atomic():
                # Update certification fields
                certification.name = data.get('name', '').strip()
                certification.organization = data.get('organization', '').strip()
                certification.credential_id = data.get('credential_id', '').strip()
                certification.credential_url = data.get('credential_url', '').strip()
                certification.description = data.get('description', '').strip()
                certification.does_not_expire = data.get('does_not_expire', False)
                
                # Handle dates
                issued_date = data.get('issued_date')
                if issued_date:
                    certification.issued_date = datetime.strptime(issued_date, '%Y-%m-%d').date()
                else:
                    certification.issued_date = None
                    
                expiry_date = data.get('expiry_date')
                if expiry_date and not certification.does_not_expire:
                    certification.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                else:
                    certification.expiry_date = None
                
                # Validation
                if not certification.name or not certification.organization:
                    return JsonResponse({
                        'success': False,
                        'error': 'Certification name and organization are required.'
                    })
                
                if certification.issued_date and certification.expiry_date:
                    if certification.issued_date > certification.expiry_date:
                        return JsonResponse({
                            'success': False,
                            'error': 'Issue date cannot be later than expiry date.'
                        })
                
                if not certification.does_not_expire and not certification.expiry_date:
                    return JsonResponse({
                        'success': False,
                        'error': 'Please provide an expiry date or check "This certification does not expire".'
                    })
                
                certification.save()
                request.user.profile_updated = timezone.now()
                request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Certification updated successfully!',
                'certification': {
                    'id': certification.id,
                    'name': certification.name,
                    'organization': certification.organization,
                    'credential_id': certification.credential_id,
                    'credential_url': certification.credential_url,
                    'issued_date': certification.issued_date.strftime('%Y-%m-%d') if certification.issued_date else '',
                    'expiry_date': certification.expiry_date.strftime('%Y-%m-%d') if certification.expiry_date else '',
                    'does_not_expire': certification.does_not_expire,
                    'description': certification.description,
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid data format.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while updating the certification.'
            })


@jobseeker_login_required
@require_http_methods(["POST"])
def delete_certification_modal(request, certification_id):
    """Delete certification via AJAX"""
    try:
        certification = Certification.objects.get(id=certification_id, user=request.user)
    except Certification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Certification not found'
        }, status=404)
    
    with transaction.atomic():
        # Delete the certification (it's linked to user via ForeignKey)
        certification.delete()
        
        # Update user's profile timestamp
        request.user.profile_updated = timezone.now()
        request.user.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Certification deleted successfully'
    })

# Resume Management Functions

@jobseeker_login_required
@require_http_methods(["POST"])
def upload_resume_modal(request):
    """Upload resume via AJAX modal form using django-storages"""
    try:
        if 'resume' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No resume file provided'
            })
        
        resume_file = request.FILES['resume']
        
        # Validate file format
        supported_formats = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            'application/pdf',  # .pdf
            'application/rtf',  # .rtf
            'application/x-rtf',  # .rtf
            'text/richtext',  # .rtf
            'application/msword',  # .doc
            'application/vnd.oasis.opendocument.text',  # .odt
            'application/x-vnd.oasis.opendocument.text',  # .odt
        ]
        
        file_type = resume_file.content_type
        file_size_kb = resume_file.size / 1024
        
        # Validate file type
        if file_type not in supported_formats:
            return JsonResponse({
                'success': False,
                'error': 'Please upload a valid file format (DOC, DOCX, PDF, RTF, ODT)'
            })
        
        # Validate file size (max 1000KB)
        if file_size_kb > 1000 or file_size_kb <= 0:
            return JsonResponse({
                'success': False,
                'error': 'File size must be between 1KB and 1000KB'
            })
        
        try:
            # Delete old resume if exists
            if request.user.resume:
                request.user.resume.delete(save=False)
            
            # Save new resume using FileField - django-storages handles S3 automatically
            request.user.resume = resume_file
            request.user.profile_updated = timezone.now()
            
            # Extract resume data (optional - keep existing functionality)
            try:
                handle_uploaded_file(resume_file, resume_file.name)
                email, mobile, text = get_resume_data(resume_file)
                request.user.resume_text = text
                
                # Update mobile if not set
                if not request.user.mobile and mobile:
                    request.user.mobile = mobile
                    
            except Exception as e:
                # Continue even if text extraction fails
                pass
            
            request.user.save()
            
            # Get resume URL directly from FileField
            resume_url = request.user.resume.url if request.user.resume else None
            
            return JsonResponse({
                'success': True,
                'message': 'Resume uploaded successfully!',
                'data': {
                    'resume_name': resume_file.name,
                    'resume_url': resume_url,
                    'file_size': f"{file_size_kb:.1f} KB",
                    'upload_date': timezone.now().strftime('%B %d, %Y'),
                    'profile_completion': request.user.profile_completion_percentage
                }
            })
            
        except Exception as upload_error:
            return JsonResponse({
                'success': False,
                'error': f'Failed to upload resume: {str(upload_error)}'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred while uploading your resume: {str(e)}'
        })


@jobseeker_login_required
@require_http_methods(["POST"])
def delete_resume_modal(request):
    """Delete resume via AJAX"""
    try:
        if not request.user.resume:
            return JsonResponse({
                'success': False,
                'error': 'No resume found to delete'
            })
        
        # Delete resume file
        request.user.resume.delete(save=False)
        
        # Clear resume-related fields
        request.user.resume_text = ""
        request.user.resume_title = ""
        request.user.profile_updated = timezone.now()
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Resume deleted successfully!',
            'data': {
                'profile_completion': request.user.profile_completion_percentage
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred while deleting your resume: {str(e)}'
        })


@jobseeker_login_required
@require_http_methods(["GET"])
def get_resume_info(request):
    """Get current resume information"""
    try:
        if not request.user.resume:
            return JsonResponse({
                'success': True,
                'has_resume': False,
                'data': None
            })
        
        # Get resume URL and filename directly from FileField
        try:            
            # Check if we have a resume file
            if not request.user.resume or not request.user.resume.name:
                return JsonResponse({
                    'success': True,
                    'has_resume': False,
                    'data': None
                })
            
            resume_url = request.user.resume.url
            resume_filename = os.path.basename(request.user.resume.name)
        except Exception as file_error:
            # If there's an issue accessing the file (e.g., file doesn't exist in storage)
            # This commonly happens in development when S3 is not properly configured
            return JsonResponse({
                'success': False,
                'error': f'Resume file not accessible. This may be due to storage configuration. Error: {str(file_error)}'
            })
        
        return JsonResponse({
            'success': True,
            'has_resume': True,
            'data': {
                'resume_name': resume_filename,
                'resume_url': resume_url,
                'upload_date': request.user.profile_updated.strftime('%B %d, %Y') if request.user.profile_updated else 'Unknown',
                'profile_completion': request.user.profile_completion_percentage
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred while getting resume information: {str(e)}'
        })


@jobseeker_login_required
@require_http_methods(["POST"])
def update_resume_modal(request):
    """Update existing resume via AJAX modal form"""
    try:
        if 'resume' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No resume file provided'
            })
        
        resume_file = request.FILES['resume']
        
        # Validate file format
        supported_formats = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            'application/pdf',  # .pdf
            'application/rtf',  # .rtf
            'application/x-rtf',  # .rtf
            'text/richtext',  # .rtf
            'application/msword',  # .doc
            'application/vnd.oasis.opendocument.text',  # .odt
            'application/x-vnd.oasis.opendocument.text',  # .odt
        ]
        
        file_type = resume_file.content_type
        file_size_kb = resume_file.size / 1024
        
        # Validate file type
        if file_type not in supported_formats:
            return JsonResponse({
                'success': False,
                'error': 'Please upload a valid file format (DOC, DOCX, PDF, RTF, ODT)'
            })
        
        # Validate file size (max 1000KB)
        if file_size_kb > 1000 or file_size_kb <= 0:
            return JsonResponse({
                'success': False,
                'error': 'File size must be between 1KB and 1000KB'
            })
        
        # Upload new resume using the FileField
        try:
            # Delete old resume if exists
            if request.user.resume:
                request.user.resume.delete(save=False)
            
            # Save new resume using FileField - django-storages handles S3 automatically
            request.user.resume = resume_file
            request.user.profile_updated = timezone.now()
            
            # Extract resume data
            try:
                handle_uploaded_file(resume_file, resume_file.name)
                email, mobile, text = get_resume_data(resume_file)
                request.user.resume_text = text
                
                # Update mobile if not set
                if not request.user.mobile and mobile:
                    request.user.mobile = mobile
                    
            except Exception as e:
                # Continue even if text extraction fails
                pass
            
            request.user.save()
            
            # Get resume URL directly from FileField
            resume_url = request.user.resume.url if request.user.resume else None
            
            return JsonResponse({
                'success': True,
                'message': 'Resume updated successfully!',
                'data': {
                    'resume_name': resume_file.name,
                    'resume_url': resume_url,
                    'file_size': f"{file_size_kb:.1f} KB",
                    'upload_date': timezone.now().strftime('%B %d, %Y'),
                    'profile_completion': request.user.profile_completion_percentage
                }
            })
            
        except Exception as upload_error:
            return JsonResponse({
                'success': False,
                'error': f'Failed to update resume: {str(upload_error)}'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred while updating your resume: {str(e)}'
        })


@jobseeker_login_required
@require_http_methods(["POST"])
def edit_basic_profile(request):
    """AJAX view to update basic profile information (job_role, current_city, experience)"""
    try:
        data = json.loads(request.body)
        user = request.user
        
        with transaction.atomic():
            # Update job role
            job_role = data.get('job_role', '').strip()
            user.job_role = job_role
            
            # Update current city
            current_city_id = data.get('current_city', '').strip()
            if current_city_id:
                try:
                    current_city = City.objects.get(id=current_city_id, status='Enabled')
                    user.current_city = current_city
                except City.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid city selected.'
                    })
            else:
                user.current_city = None
            
            # Update experience (year and month)
            year = data.get('year', '').strip()
            month = data.get('month', '').strip()
            
            user.year = year if year else ''
            user.month = month if month else ''
            
            # Update profile completeness
            user.profile_completeness = user.profile_completion_percentage
            user.profile_updated = timezone.now()
            
            user.save()
            
            # Prepare response data
            response_data = {
                'job_role': user.job_role,
                'current_city': f"{user.current_city.name}, {user.current_city.state.name}" if user.current_city else '',
                'year': user.year,
                'month': user.month,
                'profile_completion': user.profile_completion_percentage
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully!',
                'data': response_data
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data provided.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred while updating your profile: {str(e)}'
        })
