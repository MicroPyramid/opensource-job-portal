"""
Communication Views
Handles email templates, messaging, and communication features
"""
import json
import urllib
import requests
import math
import random
import time
from mpcomp.s3_utils import S3Connection
import csv
from collections import OrderedDict

from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.template import loader, Template, Context
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.hashers import check_password
from django.db.models import Q, Count
from django.contrib.auth import update_session_auth_hash
from django.template.defaultfilters import slugify
from django.contrib.auth.models import Permission, ContentType
from django.db.models import Case, When
import boto3
from django.contrib.auth import load_backend


from mpcomp.aws import AWS
from dashboard.tasks import sending_mail, send_email
from django.utils.crypto import get_random_string
from mpcomp.facebook import GraphAPI, get_access_token_from_code
from mpcomp.views import get_absolute_url
from pjob.views import save_codes_and_send_mail
from peeldb.models import (
    Country,
    JobPost,
    MetaData,
    State,
    City,
    Skill,
    Industry,
    Qualification,
    AppliedJobs,
    User,
    JOB_TYPE,
    FunctionalArea,
    Keyword,
    UserEmail,
    MARTIAL_STATUS,
    Google,
    Facebook,
    Company,
    MailTemplate,
    SentMail,
    InterviewLocation,
    COMPANY_TYPES,
    Menu,
    Ticket,
    AGENCY_INVOICE_TYPE,
    AGENCY_JOB_TYPE,
    AgencyCompany,
    AgencyRecruiterJobposts,
    AGENCY_RECRUITER_JOB_TYPE,
    AgencyApplicants,
    AgencyResume,
    POST,
    UserMessage,
)
from recruiter.forms import (
    JobPostForm,
    YEARS,
    MONTHS,
    Company_Form,
    User_Form,
    ChangePasswordForm,
    PersonalInfoForm,
    MobileVerifyForm,
    MailTemplateForm,
    EditCompanyForm,
    RecruiterForm,
    MenuForm,
    ApplicantResumeForm,
    ResumeUploadForm,
)

from mpcomp.views import (
    rand_string,
    recruiter_login_required,
    get_prev_after_pages_count,
    agency_admin_login_required,
    get_next_month,
    get_aws_file_path,
    get_resume_data,
    handle_uploaded_file,
)


# Communication Views will be moved here
# TODO: Move the following functions from the main views.py:
# - new_template()
# - edit_template()
# - emailtemplates()
# - view_template()
# - delete_template()
# - send_mail()
# - sent_mails()
# - view_sent_mail()
# - delete_sent_mail()
# - enable_email_notifications()
# - messages()



@recruiter_login_required
def new_template(request, jobpost_id):
    if request.method == "POST":
        validate_mailtemplate = MailTemplateForm(request.POST)
        if validate_mailtemplate.is_valid():
            MailTemplate.objects.create(
                title=request.POST.get("title"),
                subject=request.POST.get("subject"),
                message=request.POST.get("message"),
                created_on=datetime.utcnow(),
                modified_on=datetime.utcnow(),
                created_by=request.user,
                job_post_id=jobpost_id,
            )
            data = {
                "error": False,
                "message": "Successfully saved new template, now you can see it, edit it, send to your contacts.!",
            }
            return HttpResponse(json.dumps(data))
        data = {"error": True, "message": validate_mailtemplate.errors}
        return HttpResponse(json.dumps(data))
    return render(
        request, "recruiter/mail/new_mailtemplate.html", {"jobpost_id": jobpost_id}
    )




@recruiter_login_required
def edit_template(request, jobpost_id, template_id):
    mailtemplates = MailTemplate.objects.filter(id=template_id, created_by=request.user)
    if mailtemplates:
        mailtemplate = mailtemplates[0]
        if request.method == "POST":
            validate_mailtemplate = MailTemplateForm(
                request.POST, instance=mailtemplate
            )
            if validate_mailtemplate.is_valid():
                mailtemplate = validate_mailtemplate.save(commit=False)
                mailtemplate.modified_on = datetime.utcnow()
                mailtemplate.job_post_id = jobpost_id
                mailtemplate.save()
                data = {
                    "error": False,
                    "message": "Successfully saved template, now you can see it, edit it, send to recruiters!",
                }
                return HttpResponse(json.dumps(data))
            data = {"error": True, "message": validate_mailtemplate.errors}
            return HttpResponse(json.dumps(data))
        return render(
            request,
            "recruiter/mail/edit_mailtemplate.html",
            {"email_template": mailtemplate, "jobpost_id": jobpost_id},
        )
    message = "Sorry, the page you requested can not be found"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )




def emailtemplates(request, jobpost_id):
    mailtemplates = MailTemplate.objects.filter(created_by=request.user)
    jobpost = JobPost.objects.get(id=jobpost_id)
    return render(
        request,
        "recruiter/mail/list.html",
        {"mailtemplates": mailtemplates, "jobpost_id": jobpost_id, "jobpost": jobpost},
    )



@recruiter_login_required
def view_template(request, template_id):
    mailtemplate = MailTemplate.objects.filter(
        id=template_id, created_by=request.user
    ).first()
    if mailtemplate:
        return render(
            request, "recruiter/mail/view.html", {"mailtemplate": mailtemplate}
        )
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )




@recruiter_login_required
def delete_template(request, template_id):
    mailtemplate = MailTemplate.objects.filter(id=template_id, created_by=request.user)
    if mailtemplate.exists():
        mailtemplate.delete()
        data = {"error": False, "response": "Job Post deleted Successfully"}
        return HttpResponse(json.dumps(data))
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )


@recruiter_login_required
def send_mail(request, template_id, jobpost_id):
    mailtemplates = MailTemplate.objects.filter(id=template_id)
    if mailtemplates:
        emailtemplate = mailtemplates[0]
        if request.method == "POST":
            validate_mailtemplate = MailTemplateForm(
                request.POST, instance=emailtemplate
            )
            if validate_mailtemplate.is_valid():
                validate_mailtemplate.save()
                t = loader.get_template("email/email_template.html")
                c = {"text": emailtemplate.message}
                rendered = t.render(c)
                mto = []
                for recruiter in request.POST.getlist("recruiters"):
                    recruiter = User.objects.get(id=recruiter)
                    mto.append(recruiter.email)
                sent_mail = SentMail.objects.create(
                    template=emailtemplate, job_post_id=jobpost_id
                )

                for recruiter in request.POST.getlist("recruiters"):
                    recruiter = User.objects.get(id=recruiter)
                    sent_mail.recruiter.add(recruiter)
                subject = emailtemplate.subject
                send_email.delay(mto, subject, rendered)
                sending_mail.delay(emailtemplate, request.POST.getlist("recruiters"))
                data = {"error": False, "response": "Email Sent Successfully"}
                return HttpResponse(json.dumps(data))
            data = {"error": True, "response": validate_mailtemplate.errors}
            return HttpResponse(json.dumps(data))
        applicants = AppliedJobs.objects.filter(job_post_id=jobpost_id)
        return render(
            request,
            "recruiter/mail/send_mail.html",
            {
                "applicants": applicants,
                "mailtemplate": emailtemplate,
                "jobpost_id": jobpost_id,
            },
        )
    else:
        reason = "The URL may be misspelled or the page you're looking for is no longer available."
        return render(
            request,
            "recruiter/404.html",
            {
                "message_type": "404",
                "message": "Sorry, the page you requested can not be found",
                "reason": reason,
            },
            status=404,
        )




@recruiter_login_required
def sent_mails(request, jobpost_id):
    sent_mails = SentMail.objects.filter(job_post=jobpost_id)
    return render(
        request,
        "recruiter/mail/sent_mail_list.html",
        {"sent_mails": sent_mails, "jobpost_id": jobpost_id},
    )




def view_sent_mail(request, sent_mail_id):
    sent_mail = SentMail.objects.filter(id=sent_mail_id).first()
    if sent_mail:
        return render(
            request, "recruiter/mail/view_sent_mail.html", {"sent_mail": sent_mail}
        )
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )




@recruiter_login_required
def delete_sent_mail(request, sent_mail_id):
    sent_mails = SentMail.objects.filter(id=sent_mail_id)
    if sent_mails:
        sent_mail = sent_mails[0]
        sent_mail.delete()
        data = {"error": False, "response": "Sent Mail Deleted Successfully"}
        return HttpResponse(json.dumps(data))
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )



@recruiter_login_required
def enable_email_notifications(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    if job_post.send_email_notifications:
        job_post.send_email_notifications = False
    else:
        job_post.send_email_notifications = True
    job_post.save()
    return HttpResponseRedirect(
        reverse("recruiter:view", kwargs={"job_post_id": job_post_id})
    )




@recruiter_login_required
def messages(request):
    if request.GET.get("search"):
        user_ids = AppliedJobs.objects.filter(
            job_post__user__id=request.user.id
        ).values_list("user", flat=True)
        users = User.objects.filter(
            Q(id__in=user_ids)
            & Q(
                Q(email__icontains=request.GET.get("search"))
                | Q(first_name__icontains=request.GET.get("search"))
                | Q(last_name__icontains=request.GET.get("search"))
            )
        )
        return HttpResponse(
            json.dumps(
                {"error": False, "users": list(users.values_list("id", flat=True))}
            )
        )
    if request.POST.get("mode") == "get_messages":
        UserMessage.objects.filter(
            message_to=request.user.id,
            message_from=int(request.POST.get("r_id")),
            job=None,
        ).update(is_read=True)

        m1 = UserMessage.objects.filter(
            message_from=request.user.id,
            message_to=int(request.POST.get("r_id")),
            job=None,
        )

        m2 = UserMessage.objects.filter(
            message_to=request.user.id,
            message_from=int(request.POST.get("r_id")),
            job=None,
        )

        messages = list(m1) + list(m2)

        user = User.objects.filter(id=request.POST.get("r_id")).first()
        if user:
            try:
                user_pic = user.profile_pic.url
            except:
                user_pic = user.photo
            try:
                profile_pic = request.user.profile_pic.url
            except:
                profile_pic = request.user.photo
            if not user_pic:
                user_pic = "https://cdn.peeljobs.com/dummy.jpg"
            if not profile_pic:
                profile_pic = "https://cdn.peeljobs.com/dummy.jpg"
            messages = render_to_string(
                "candidate/messages.html",
                {
                    "messages": list(messages),
                    "user": user,
                    "user_pic": user_pic,
                    "profile_pic": profile_pic,
                },
                request,
            )
            return HttpResponse(json.dumps({"error": False, "messages": messages}))
        else:
            return HttpResponse(
                json.dumps({"error": True, "response": "User Not Found!"})
            )
    if request.POST.get("post_message"):
        msg = UserMessage.objects.create(
            message=request.POST.get("message"),
            message_from=request.user,
            message_to=User.objects.get(id=int(request.POST.get("message_to"))),
        )

        if request.POST.get("job_id"):
            msg.job__id = int(request.POST.get("job_id"))
            msg.save()

        time = datetime.now().strftime("%b. %d, %Y, %l:%M %p")
        return HttpResponse(
            json.dumps(
                {
                    "error": False,
                    "message": request.POST.get("message"),
                    "msg_id": msg.id,
                    "time": time,
                }
            )
        )
    if request.POST.get("mode") == "delete_message":
        msg = UserMessage.objects.get(id=request.POST.get("id"))
        if msg.message_from == request.user or msg.message_to == request.user:
            UserMessage.objects.get(id=request.POST.get("id")).delete()
            data = {"error": False, "message": request.POST.get("message")}
        else:
            data = {"error": True, "message": "You Cannot delete!"}
        return HttpResponse(json.dumps(data))
    if request.POST.get("mode") == "delete_chat":
        if request.POST.get("job"):
            UserMessage.objects.filter(
                message_from=request.user.id,
                message_to=int(request.POST.get("user")),
                job=int(request.POST.get("job")),
            ).delete()

            UserMessage.objects.filter(
                message_to=request.user.id,
                message_from=int(request.POST.get("user")),
                job=int(request.POST.get("job")),
            ).delete()

        else:
            UserMessage.objects.filter(
                message_from=request.user.id,
                message_to=int(request.POST.get("user")),
                job=None,
            ).delete()

            UserMessage.objects.filter(
                message_to=request.user.id,
                message_from=int(request.POST.get("user")),
                job=None,
            ).delete()

        return HttpResponse(
            json.dumps({"error": False, "message": request.POST.get("message")})
        )
    if request.user.is_authenticated:
        messages = UserMessage.objects.filter(
            Q(message_from=request.user.id) | Q(message_to=request.user.id)
        )

        user_ids = AppliedJobs.objects.filter(
            job_post__user__id=request.user.id
        ).values_list("user", flat=True)
        users = User.objects.filter(id__in=user_ids)
        if messages:
            recruiter_ids = list(
                messages.values_list("message_from", flat=True).distinct()
            ) + list(messages.values_list("message_to", flat=True).distinct())

            preserved = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(recruiter_ids)]
            )
            users = users.order_by(preserved)
        return render(request, "recruiter/user/messages.html", {"users": users})
    else:
        return HttpResponseRedirect("/")

