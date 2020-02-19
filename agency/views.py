import json
import math
from datetime import datetime
from math import ceil

from django.urls import reverse
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from mpcomp.views import (float_round, get_prev_after_pages_count,
                          recruiter_login_required)
from peeldb.models import (MONTHS, POST, AgencyApplicants, AgencyCompany,
                           AgencyCompanyBranch, AgencyRecruiterJobposts,
                           AgencyResume, AgencyWorkLog, AppliedJobs, City,
                           JobPost, Skill, User)
from recruiter.forms import (YEARS, AgencyWorkLogForm, ClientForm)


# Create your views here.
@recruiter_login_required
def client_list(request):
    clients = AgencyCompany.objects.filter(company=request.user.company)
    if request.method == 'POST':
        if request.POST['search_text']:
            clients = clients.filter(Q(name__icontains=request.POST['search_text']) | Q(
                website__icontains=request.POST['search_text']))
        if request.POST['location']:
            branches = AgencyCompanyBranch.objects.filter(
                location_id=request.POST['location'])
            clients = clients.filter(branch_details__in=branches)
    if "page" in request.GET and int(request.GET.get('page')) > 0:
        page = int(request.GET.get('page'))
    else:
        page = 1
    items_per_page = 10
    cities = City.objects.filter(status='Enabled')
    no_pages = int(math.ceil(float(clients.count()) / items_per_page))
    clients = clients[(page - 1) * items_per_page:page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages)
    return render(request, 'recruiter/company/client_list.html', {'clients': clients,
                                                                  'aft_page': aft_page,
                                                                  'after_page': after_page,
                                                                  'prev_page': prev_page,
                                                                  'previous_page': previous_page,
                                                                  'current_page': page, 'last_page': no_pages,
                                                                  'search_value': request.GET['search'] if 'search' in request.GET.keys() else '',
                                                                  'cities': cities})


def client_errors(errors, data):
    for key in data.keys():
        if 'location_' in key and len(data[key]) == 0:
            errors[key] = 'This field is required'
        if 'address_' in key and len(data[key]) == 0:
            errors[key] = 'This field is required'
        if 'contact_details_' in key and not data[key]:
            errors[key] = 'This field is required'
        if 'name_' in key and not data[key]:
            errors[key] = 'This field is required'
        if 'percantage_' in key and not data[key]:
            errors[key] = 'This field is required'
    return errors


@recruiter_login_required
def add_client(request):
    if request.user.is_agency_admin:
        if request.method == 'POST':
            validate_client = ClientForm(
                request.POST, request.FILES, user=request.user)
            errors = client_errors(validate_client.errors, request.POST)
            if not errors:
                client = AgencyCompany.objects.create(name=request.POST.get('name'), website=request.POST.get(
                    'website'), company=request.user.company, logo=request.FILES.get('profile_pic'),
                    decription=request.POST.get('decription'), created_by=request.user)
                for each in range(1, int(request.POST.get('no_of_branch')) + 1):
                    if request.POST.get('location_' + str(each)):
                        city = City.objects.get(
                            id=request.POST.get('location_' + str(each)))
                        address = request.POST.get('address_' + str(each))
                        contact_details = request.POST.get(
                            'contact_details_' + str(each))
                        is_major = request.POST.get(
                            'is_major_' + str(each), '')
                        company_branch = AgencyCompanyBranch.objects.create(
                            location=city, address=address, contact_details=contact_details)
                        company_branch.is_major = is_major == 'on'
                        company_branch.save()
                        client.branch_details.add(company_branch)
                # for each in range(1, int(request.POST.get('no_of_category')) + 1):
                #     if 'name_' + str(each) in request.POST.keys() and len(request.POST.get('name_' + str(each))) > 0:
                #         name = request.POST.get('name_' + str(each))
                #         company_category = AgencyCompanyCatogery.objects.create(
                #             name=name)
                #         if ('percantage_' + str(each)) in request.POST.keys():
                #             company_category.percantage = request.POST.get(
                #                 'percantage_' + str(each))
                #             company_category.save()
                #         client.company_categories.add(company_category)
                data = {'error': False, 'response': 'Client Created Successfully'}
            else:
                data = {'error': True, 'response': errors}
            return HttpResponse(json.dumps(data))
        cities = City.objects.filter(status='Enabled')
        return render(request, 'recruiter/company/add_client.html', {'cities': cities,
                                                                     'months': MONTHS})
    else:
        message = "Sorry, You Don't have access to this page"
        return render(request, 'recruiter/recruiter_404.html', {'message': message}, status=404)


@recruiter_login_required
def edit_client(request, client_id):
    if request.user.is_agency_admin:
        client = AgencyCompany.objects.filter(
            id=client_id, company=request.user.company).first()
        if client:
            if request.method == 'GET':
                cities = City.objects.filter(status='Enabled')
                return render(request, 'recruiter/company/edit_client.html', {'client': client,
                                                                              'cities': cities,
                                                                              'months': MONTHS})
            validate_client = ClientForm(
                request.POST, request.FILES, instance=client, user=request.user)
            errors = client_errors(validate_client.errors, request.POST)
            if not errors:
                client = validate_client.save(commit=False)
                if request.FILES.get('profile_pic'):
                    client.profile_pic = request.FILES.get('profile_pic')
                client.save()
                client.branch_details.clear()
                client.company_categories.clear()
                for each in range(1, int(request.POST.get('no_of_branch')) + 1):
                    address = request.POST.get('address_' + str(each))
                    contact_details = request.POST.get(
                        'contact_details_' + str(each))
                    is_major = request.POST.get(
                        'is_major_' + str(each), '')
                    if request.POST.get('location_' + str(each)) and address and contact_details:
                        city = City.objects.get(
                            id=request.POST.get('location_' + str(each)))
                        company_branch = AgencyCompanyBranch.objects.create(
                            location=city, address=address, contact_details=contact_details)
                        company_branch.is_major = is_major == 'on'
                        company_branch.save()
                        client.branch_details.add(company_branch)
                data = {'error': False, 'response': 'Client Updated Successfully'}
            else:
                data = {'error': True, 'response': errors}
            return HttpResponse(json.dumps(data))
    message = 'Sorry, No Client Available with this id'
    return render(request, 'recruiter/recruiter_404.html', {'message': message}, status=404)


@recruiter_login_required
def delete_client(request, client_id):
    user = request.user
    if user.is_agency_admin:
        client = AgencyCompany.objects.filter(
            id=client_id, company=user.company)
        if client:
            client = client[0]
            client.delete()
            data = {'error': False, 'response': 'Client Deleted Successfully'}
        else:
            data = {'error': True, 'response': 'Some Problem Occurs'}
    else:
        data = {
            'error': True, 'response': 'Only Company Admin can delete their clients'}
    return HttpResponse(json.dumps(data))


@recruiter_login_required
def client_profile(request, client_id):
    client = AgencyCompany.objects.filter(
        id=client_id, company=request.user.company)
    if client:
        client = client[0]
        return render(request, "recruiter/company/client_view.html", {'client': client})
    message = 'Sorry, No Client Available with this id'
    return render(request, 'recruiter/recruiter_404.html', {'message': message}, status=404)


@recruiter_login_required
def add_branch(request, branch_id):
    cities = City.objects.filter(status='Enabled')
    branch_id = int(branch_id) + 1
    return render(request, "recruiter/company/add_branch.html", {'branch_id': branch_id, 'cities': cities})


@recruiter_login_required
def add_contract_deatils(request, contact_details_id):
    contact_details_id = int(contact_details_id) + 1
    return render(request, "recruiter/company/add_contract_details.html", {'months': MONTHS, 'contact_details_id': contact_details_id})


@recruiter_login_required
def delete_resume(request, resume_id):
    user = request.user
    if user.is_agency_admin:
        agency_resumes = AgencyResume.objects.filter(id=resume_id)
    else:
        agency_resumes = AgencyResume.objects.filter(
            id=resume_id, uploaded_by=request.user)
    if agency_resumes:
        agency_resumes.delete()
        data = {'error': False, 'data': 'Resume Deleted Successfully'}
    else:
        data = {'error': True, 'data': 'Error While Deleting Resume'}
    return HttpResponse(json.dumps(data))


@recruiter_login_required
def dashboard(request):
    if request.user.is_agency_admin:
        job_posts = JobPost.objects.filter(user__company=request.user.company)
    else:
        job_posts = JobPost.objects.filter(
            agency_recruiters__in=[request.user])
    if request.user.is_agency_admin:
        agency_resumes = AgencyResume.objects.filter(
            uploaded_by__company=request.user.company)
    else:
        agency_resumes = AgencyResume.objects.filter(uploaded_by=request.user)
    no_of_jobs = len(job_posts)
    items_per_page = 10
    no_pages = int(math.ceil(float(len(job_posts)) / items_per_page))

    try:
        if int(request.GET.get('page')) > (no_pages + 2):
            page = 1
            return HttpResponseRedirect(reverse('jobs:index'))
        else:
            page = int(request.GET.get('page'))
    except:
        page = 1
    job_posts = job_posts[(page - 1) * items_per_page:page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages)

    return render(request, 'recruiter/company/dashboard.html', {'agency_resumes': agency_resumes,
                                                                'aft_page': aft_page,
                                                                'after_page': after_page,
                                                                'prev_page': prev_page,
                                                                'previous_page': previous_page,
                                                                'current_page': page,
                                                                'last_page': no_pages,
                                                                'no_of_jobs': no_of_jobs,
                                                                'job_posts': job_posts
                                                                })


@recruiter_login_required
def applicant_status_change(request, applicant_id):
    applicant = get_object_or_404(AppliedJobs, id=applicant_id)
    if request.POST:
        applicant.status = request.POST.get('applicant_status')
        applicant.save()
    return HttpResponse(json.dumps({'error': False, 'response': 'Status Changed Successfully'}))


@recruiter_login_required
def delete_applicant_status(request, applicant_id):
    applicant = AppliedJobs.objects.filter(id=applicant_id)
    if applicant:
        applicant.delete()
        data = {'error': False, 'response': 'JobPost deleted Successfully'}
    else:
        data = {'error': True, 'response': 'Some Problem Occurs'}
    return HttpResponse(json.dumps(data))


@recruiter_login_required
def view_resumes(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    selected_skills = []
    agency_resumes = AppliedJobs.objects.filter(job_post=job_post)

    if request.POST.get('recruiters'):
        agency_resumes = agency_resumes.filter(
            applicant__uploaded_by_id=request.POST.get('recruiters'))
    if request.POST.get('experience'):
        agency_resumes = agency_resumes.filter(
            applicant__experience=request.POST.get('experience'))
    if request.POST.getlist('skills'):
        skills = Skill.objects.filter(id__in=request.POST.getlist('skills'))
        agency_resumes = agency_resumes.filter(applicant__skill__in=skills)
        selected_skills = request.POST.getlist('skills')

    if request.POST.get('apply_job'):
        if request.POST.get('jobposts_type'):

            for each in request.POST.getlist('apply_job'):
                agency_applicant = AgencyApplicants.objects.get(
                    id=each, job_post=job_post)
                agency_applicant.status = request.POST.get('jobposts_type')
                agency_applicant.save()

                agency_applicant.applicant.status = 'Pending'
                agency_applicant.applicant.save()

            if str(request.POST.get('jobposts_type')) == 'Hired':
                applicants = AgencyApplicants.objects.filter(
                    id__in=request.POST.getlist('apply_job')).values_list('applicant', flat=True)
                applicant_agency_resumes = AgencyResume.objects.filter(
                    id__in=applicants)
                applicant_agency_resumes.update(
                    status=request.POST.get('jobposts_type'))

    no_of_jobs = len(agency_resumes)
    items_per_page = 10
    no_pages = int(math.ceil(float(len(agency_resumes)) / items_per_page))

    try:
        if int(request.GET.get('page')) > (no_pages + 2):
            page = 1
            return HttpResponseRedirect(reverse('jobs:index'))
        else:
            page = int(request.GET.get('page'))
    except:
        page = 1
    agency_resumes = agency_resumes[
        (page - 1) * items_per_page:page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages)
    skills = Skill.objects.filter(status='Active')
    recruiters = User.objects.filter(company=request.user.company)
    return render(request, "recruiter/company/job_resume_view.html", {'job_post': job_post,
                                                                      'agency_resumes': agency_resumes,
                                                                      'recruiters': recruiters,
                                                                      'years': YEARS,
                                                                      'skills': skills,
                                                                      'aft_page': aft_page,
                                                                      'after_page': after_page,
                                                                      'prev_page': prev_page,
                                                                      'previous_page': previous_page,
                                                                      'current_page': page,
                                                                      'last_page': no_pages,
                                                                      'no_of_jobs': no_of_jobs,
                                                                      'status': POST,
                                                                      'selected_skills': selected_skills
                                                                      })


@recruiter_login_required
def job_status_change(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    agency_jobposts = AgencyRecruiterJobposts.objects.filter(job_post=job_post)
    if agency_jobposts:
        agency_jobpost = agency_jobposts[0]
        agency_jobpost.status = 'Hired'
        agency_jobpost.message = request.POST.get('message')
        agency_jobpost.save()
        job_post.status = 'Hired'
        job_post.save()
        return HttpResponseRedirect(reverse('agency:view', kwargs={'job_post_id': job_post_id}))


@recruiter_login_required
def jobs_billing_process(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    if request.user.is_agency_admin:

        agreed_percantage = job_post.agency_category.percantage
        total_amount = job_post.agency_amount

        service_tax = (float(total_amount) * 14)/100.0
        swatch_barath_cess = (float(total_amount) * 0.5)/100.0
        krushi_kalyani_cess = (float(total_amount) * 0.5)/100.0
        agreed_percantage_amount = (
            float(total_amount)*float(agreed_percantage))/100.0

        service_tax = float_round(service_tax, 2, ceil)
        swatch_barath_cess = float_round(swatch_barath_cess, 2, ceil)
        krushi_kalyani_cess = float_round(krushi_kalyani_cess, 2, ceil)
        agreed_percantage_amount = float_round(
            agreed_percantage_amount, 2, ceil)

        deducted_ammount = float(service_tax)+float(swatch_barath_cess) + \
            float(krushi_kalyani_cess)+float(agreed_percantage_amount)
        total_invoice_amount = float(total_amount) - deducted_ammount

        # import pdfkit
        data = {'agreed_percantage': agreed_percantage,
                'total_amount': total_amount, 'service_tax': service_tax,
                'swatch_barath_cess': swatch_barath_cess, 'krushi_kalyani_cess': krushi_kalyani_cess,
                'agreed_percantage_amount': agreed_percantage_amount, 'deducted_ammount': deducted_ammount,
                'total_invoice_amount': total_invoice_amount, 'job_post': job_post
                }

        # rendered_html = html_template.render(
        #     RequestContext(request, data)).encode(encoding="UTF-8")

        # pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=[])
        pdf_file = data
        http_response = HttpResponse(pdf_file, content_type='application/pdf')
        # http_response['Content-Disposition'] = 'filename="report.pdf"'

        return http_response


@recruiter_login_required
def hired_candidates(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    agency_resumes = job_post.get_hired_applicants()
    no_of_jobs = len(agency_resumes)
    items_per_page = 10
    no_pages = int(math.ceil(float(len(agency_resumes)) / items_per_page))

    try:
        if int(request.GET.get('page')) > (no_pages + 2):
            return HttpResponseRedirect(reverse('jobs:index'))
        else:
            page = int(request.GET.get('page'))
    except:
        page = 1
    agency_resumes = agency_resumes[
        (page - 1) * items_per_page:page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages)
    skills = Skill.objects.filter(status='Active')
    recruiters = User.objects.filter(company=request.user.company)
    years = YEARS
    return render(request, 'recruiter/company/jobs_hired_resumes.html', {'agency_resumes': agency_resumes,
                                                                         'recruiters': recruiters,
                                                                         'years': years,
                                                                         'skills': skills,
                                                                         'aft_page': aft_page,
                                                                         'after_page': after_page,
                                                                         'prev_page': prev_page,
                                                                         'previous_page': previous_page,
                                                                         'current_page': page,
                                                                         'last_page': no_pages,
                                                                         'no_of_jobs': no_of_jobs,
                                                                         })


@recruiter_login_required
def user_work_log(request):
    job_post = get_object_or_404(JobPost, id=request.POST['job_post'])
    validate_worklog = AgencyWorkLogForm(request.POST)
    if validate_worklog.is_valid():
        start_time = datetime.strptime(request.POST.get(
            'start_time'), '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(request.POST.get(
            'end_time'), '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

        AgencyWorkLog.objects.create(job_post=job_post, user=request.user,
                                     no_of_profiles=request.POST['no_of_profiles'],
                                     summary=request.POST['summary'],
                                     start_time=start_time, end_time=end_time,
                                     timegap=request.POST['time_gap'])
        data = {'error': False, 'response': 'WorkLog Created Successfully'}
    else:
        data = {'error': True, 'response': validate_worklog.errors}
    return HttpResponse(json.dumps(data))
