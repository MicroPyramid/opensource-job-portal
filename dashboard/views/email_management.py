import json
from datetime import datetime

from django.http.response import HttpResponse
from django.shortcuts import render
from django.template import loader

from mpcomp.views import permission_required
from peeldb.models import (
    MailTemplate,
    SentMail,
    User,
)

from ..forms import MailTemplateForm
from ..tasks import sending_mail, send_email


# Functions to move here from main views.py:

@permission_required("activity_view", "activity_edit")
def emailtemplates(request):
    mailtemplates = MailTemplate.objects.filter()
    return render(request, "dashboard/mail/list.html", {"mailtemplates": mailtemplates})


@permission_required("activity_edit")
def new_template(request):
    if request.method == "POST":
        validate_mailtemplate = MailTemplateForm(request.POST)
        if validate_mailtemplate.is_valid():
            mail_template = MailTemplate.objects.create(
                title=request.POST.get("title"),
                subject=request.POST.get("subject"),
                message=request.POST.get("message"),
                created_on=datetime.utcnow(),
                modified_on=datetime.utcnow(),
                created_by=request.user,
            )
            if str(request.POST.get("show_recruiter")) == "True":
                mail_template.show_recruiter = True
                mail_template.applicant_status = request.POST.get("applicant_status")
                mail_template.save()
            data = {
                "error": False,
                "message": "Successfully saved new template, now you can see it, edit it, send to your contacts.!",
            }
        else:
            data = {"error": True, "message": validate_mailtemplate.errors}
        return HttpResponse(json.dumps(data))
    else:
        return render(
            request, "dashboard/mail/new_mailtemplate.html", {}
        )


@permission_required("activity_edit")
def edit_template(request, template_id):
    mailtemplates = MailTemplate.objects.filter(id=template_id)
    if mailtemplates:
        mailtemplate = mailtemplates[0]
        if request.method == "POST":
            validate_mailtemplate = MailTemplateForm(
                request.POST, instance=mailtemplate
            )
            if validate_mailtemplate.is_valid():
                mailtemplate = validate_mailtemplate.save(commit=False)
                mailtemplate.modified_on = datetime.utcnow()
                if (
                    "show_recruiter" in request.POST.keys()
                    and str(request.POST.get("show_recruiter")) == "True"
                ):
                    mailtemplate.show_recruiter = True
                    mailtemplate.applicant_status = request.POST.get("applicant_status")
                else:
                    mailtemplate.show_recruiter = False
                mailtemplate.save()

                mailtemplate.save()
                data = {
                    "error": False,
                    "message": "Successfully saved template, now you can see it, edit it, send to recruiters!",
                }
            else:
                data = {"error": True, "message": validate_mailtemplate.errors}
            return HttpResponse(json.dumps(data))
        return render(
            request,
            "dashboard/mail/edit_mailtemplate.html",
            {"email_template": mailtemplate},
        )
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "dashboard/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )


@permission_required("activity_view", "activity_edit")
def view_template(request, template_id):
    mailtemplate = MailTemplate.objects.filter(id=template_id).first()
    if mailtemplate:
        return render(
            request, "dashboard/mail/view.html", {"mail_template": mailtemplate}
        )
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_edit")
def delete_template(request, template_id):
    mailtemplates = MailTemplate.objects.filter(id=template_id)
    if mailtemplates:
        mailtemplates.delete()
        data = {"error": False, "response": "Job Post deleted Successfully"}
        return HttpResponse(json.dumps(data))
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_edit")
def send_mail(request, template_id):
    mailtemplate = MailTemplate.objects.filter(id=template_id).first()
    if mailtemplate:
        if request.method == "POST":
            validate_mailtemplate = MailTemplateForm(
                request.POST, instance=mailtemplate
            )
            if validate_mailtemplate.is_valid():
                emailtemplate = mailtemplate
                t = loader.get_template("email/email_template.html")
                c = {"text": emailtemplate.message}
                subject = emailtemplate.subject
                rendered = t.render(c)
                mto = []
                for recruiter in request.POST.getlist("recruiters"):
                    recruiter = User.objects.get(id=recruiter)
                    mto.append(recruiter.email)
                sent_mail = SentMail.objects.create(template=emailtemplate)

                for recruiter in request.POST.getlist("recruiters"):
                    recruiter = User.objects.get(id=recruiter)
                    sent_mail.recruiter.add(recruiter)
                send_email.delay(mto, subject, rendered)
                sending_mail.delay(mailtemplate, request.POST.getlist("recruiters"))
                return HttpResponse(
                    json.dumps({"error": False, "response": "Email Sent Successfully"})
                )
            return HttpResponse(
                json.dumps({"error": True, "response": validate_mailtemplate.errors})
            )
        recruiters = User.objects.filter(user_type="RR")
        return render(
            request,
            "dashboard/mail/send_mail.html",
            {"recruiters": recruiters, "mailtemplate": mailtemplate},
        )
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_view", "activity_edit")
def sent_mails(request):
    sent_mails = SentMail.objects.filter()
    return render(
        request, "dashboard/mail/sent_mail_list.html", {"sent_mails": sent_mails}
    )


@permission_required("activity_view", "activity_edit")
def view_sent_mail(request, sent_mail_id):
    sent_mails = SentMail.objects.filter(id=sent_mail_id)
    if sent_mails:
        sent_mail = sent_mails[0]
        return render(
            request, "dashboard/mail/view_sent_mail.html", {"sent_mail": sent_mail}
        )
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_edit")
def delete_sent_mail(request, sent_mail_id):
    sent_mails = SentMail.objects.filter(id=sent_mail_id)
    if sent_mails:
        sent_mail = sent_mails[0]
        sent_mail.delete()
        data = {"error": False, "response": "Sent Mail Deleted Successfully"}
        return HttpResponse(json.dumps(data))
    return render(request, "dashboard/404.html", status=404)
