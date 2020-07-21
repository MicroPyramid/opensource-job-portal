"""
    Support module for recruiter, will generate a notification
    email to recruiter when admin gives suggestions
"""

import json
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template import loader

from peeldb.models import (
    Ticket,
    STATUS,
    TICKET_TYPES,
    PRIORITY_TYPES,
    Attachment,
    Comment,
)
from mpcomp.views import Memail
from .forms import TicketForm, CommentForm


@login_required
def index(request):

    """
        Method: GET
            1. Recruiter: Will display the recent tickets created by loggedin user
            and sending the priority types, ticket types to the page
            2. Admin: Sending the priority types, ticket types to the page
            3. For other users, displaying 404 page
        Method: POST
            1. Validates a post data along with ticket attachments, sends errors as json to browser
            2. Creating a ticket with its attachments in open state
            3. Sending the email to the created user with respected ticket message
    """

    if request.method == "GET":
        if request.user.is_agency_recruiter or request.user.is_recruiter:
            tickets = Ticket.objects.filter(user=request.user).order_by("-created_on")
            template_name = "recruiter/tickets/ticket.html"
            data = {
                "tickets": tickets,
                "priorities": PRIORITY_TYPES,
                "ticket_types": TICKET_TYPES,
            }
        elif request.user.is_staff:
            template_name = "dashboard/tickets/ticket.html"
            data = {"priorities": PRIORITY_TYPES, "ticket_types": TICKET_TYPES}
        else:
            template_name = "recruiter/recruiter_404.html"
            data = {
                "message": "Sorry, No Ticket Found",
                "reason": """The URL may be misspelled or the ticket
                        you're looking for is no longer available.""",
            }
        return render(request, template_name, data)
    validate_ticket = TicketForm(request.POST, request.FILES)
    if validate_ticket.is_valid():
        ticket = validate_ticket.save(commit=False)
        ticket.user = request.user
        ticket.status = "Open"
        ticket.save()
        for key, value in request.FILES.items():
            attachment = Attachment.objects.create(
                attached_file=value, uploaded_by=request.user
            )
            ticket.attachments.add(attachment)
        temp = loader.get_template("email/new_ticket.html")
        subject = "Service Request | Peeljobs"
        rendered = temp.render({"ticket": ticket})
        mfrom = settings.DEFAULT_FROM_EMAIL
        user_active = True if ticket.user.is_active else False
        Memail([ticket.user.email], mfrom, subject, rendered, user_active)
        data = {"error": False, "response": "New Ticket Created Successfully"}
    else:
        errors = validate_ticket.errors
        for key in request.POST.keys():
            if "attachment_" in key:
                errors[key] = "This field is required"
        data = {"error": True, "response": errors}
    return HttpResponse(json.dumps(data))


@login_required
def new_ticket(request):

    """
        Method: GET
            1. Recruiter: Will display create ticket page and sending the priority types,
               ticket types to the page
        Method: POST
            1. Validates a post data along with ticket attachments, sends errors as json to browser
            2. Creating a ticket with its attachments in open state
            3. Sending the email to the created user with respected ticket message

    """
    if request.method == "GET":
        return render(
            request,
            "recruiter/tickets/new_ticket.html",
            {"priorities": PRIORITY_TYPES, "ticket_types": TICKET_TYPES},
        )
    validate_ticket = TicketForm(request.POST, request.FILES)
    if validate_ticket.is_valid():
        ticket = validate_ticket.save(commit=False)
        ticket.user = request.user
        ticket.status = "Open"
        ticket.save()
        for key, value in request.FILES.items():
            attachment = Attachment.objects.create(
                attached_file=value, uploaded_by=request.user
            )
            ticket.attachments.add(attachment)
        temp = loader.get_template("email/new_ticket.html")
        subject = "Service Request | Peeljobs"
        rendered = temp.render({"ticket": ticket})
        mfrom = settings.DEFAULT_FROM_EMAIL
        user_active = True if ticket.user.is_active else False
        Memail(ticket.user.email, mfrom, subject, rendered, user_active)
        data = {"error": False, "response": "New Ticket Created Successfully"}
    else:
        errors = validate_ticket.errors
        data = {"error": True, "response": errors}
    return HttpResponse(json.dumps(data))


@login_required
def edit_ticket(request, ticket_id):
    """
        Method: GET
            1. Check for a ticket with the id mentioned in the url
            2. Recruiter: Will display edit ticket page and sending the priority types,
               ticket types to the page
            2. Dashboard: Will display edit ticket page and sending the priority types,
               ticket types to the page

        Method: POST
            1. Validates a post data along with ticket attachments, sends errors as json to browser
            2. Updates a ticket with its attachments in open state

    """
    ticket = Ticket.objects.filter(id=ticket_id, user=request.user).first()
    if request.method == "GET":
        if ticket:
            template_name = (
                "recruiter/tickets/edit_ticket.html"
                if request.user.is_agency_recruiter or request.user.is_recruiter
                else "dashboard/tickets/edit_ticket.html"
            )
            data = {
                "priorities": PRIORITY_TYPES,
                "ticket_types": TICKET_TYPES,
                "ticket": ticket,
            }
        else:
            reason = """The URL may be misspelled or the ticket
                        you're looking for is no longer available."""
            template_name = "recruiter/recruiter_404.html"
            data = {
                "message_type": "404",
                "message": "Sorry, No Ticket Found",
                "reason": reason,
            }
        return render(request, template_name, data, status=200 if ticket else 404)
    validate_ticket = TicketForm(request.POST, request.FILES, instance=ticket)
    if validate_ticket.is_valid():
        ticket = validate_ticket.save(commit=False)
        ticket.user = request.user
        ticket.status = "Open"
        ticket.save()
        for key, value in request.FILES.items():
            attachment = Attachment.objects.create(
                attached_file=value, uploaded_by=request.user
            )
            ticket.attachments.add(attachment)
        data = {"error": False, "response": "Ticket Updated Successfully"}
    else:
        errors = validate_ticket.errors
        for key in request.POST.keys():
            if "attachment_" in key:
                errors[key] = "This field is required"
        data = {"error": True, "response": errors}
    return HttpResponse(json.dumps(data))


@login_required
def delete_ticket(request, ticket_id):

    """
        Method: GET
            1. Check for a ticket existed or not with the id mentioned in the url
            2. if the ticket created user, loggedin user or wheather the user is admin,
               then deleting the ticket

    """
    tickets = Ticket.objects.filter(id=ticket_id)
    if tickets:
        ticket = tickets[0]
        if request.user.is_staff or request.user == ticket.user:
            ticket.delete()
            data = {"error": False, "response": "Ticket Deleted Successfully"}
        else:
            data = {"error": True, "response": "This Ticket cant be deleted"}
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": "This Ticket cant be deleted"}
        return HttpResponse(json.dumps(data))


@login_required
def delete_attachment(request, attachment_id):
    """
        Method: GET
            1. Check for a attachment existed or not with the id mentioned in the url
            2. if the ticket attachment created user, loggedin user or wheather the user is admin,
               then deleting the ticket attachment

    """
    attachments = Attachment.objects.filter(id=attachment_id)
    if attachments:
        attachment = attachments[0]
        if request.user.is_staff or request.user == attachment.uploaded_by:
            attachment.delete()
            data = {"error": False, "response": "Attachment Deleted Successfully"}
        else:
            data = {"error": True, "response": "This Attachment cant be deleted"}
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": "This Attachment cant be deleted"}
        return HttpResponse(json.dumps(data))


@login_required
def delete_comment(request, comment_id):

    """
        Method: GET
            1. Check for a comment existed or not with the id mentioned in the url
            2. if the ticket comment created user, loggedin user or wheather the user is admin,
               then deleting the ticket comment

    """
    comments = Comment.objects.filter(id=comment_id)
    if comments:
        comment = comments[0]
        if request.user.is_staff or request.user == comment.commented_by:
            comment.delete()
            data = {"error": False, "response": "Comment Deleted Successfully"}
        else:
            data = {"error": True, "response": "This Comment cant be deleted"}
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": "This Comment cant be deleted"}
        return HttpResponse(json.dumps(data))


TICKET_STATUS = (
    ("Open", "Open"),
    ("Closed", "Closed"),
)


@login_required
def view_ticket(request, ticket_id):

    """
        Method: GET
            1. Check for a ticket existed or not with the id mentioned in the url
            2. check the loogedin is ticket_created user or admin, If not returns a 404 page

    """

    if not request.user.user_type == "JS":
        tickets = Ticket.objects.filter(id=ticket_id, user=request.user)
        if request.method == "GET":
            if tickets:
                ticket = tickets[0]
                if request.user.is_staff or request.user == ticket.user:
                    template_name = "recruiter/tickets/view_ticket.html"
                    cloudfront_url = settings.CLOUDFRONT_DOMAIN
                    return render(
                        request,
                        template_name,
                        {
                            "priorities": PRIORITY_TYPES,
                            "ticket_types": TICKET_TYPES,
                            "ticket": tickets[0],
                            "status": STATUS,
                            "cloudfront_url": cloudfront_url,
                        },
                    )

    message = "Sorry, No Ticket Found"
    reason = "The URL may be misspelled or the ticket you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )


@login_required
def ticket_status(request, ticket_id):
    """
        1. Check for a ticket existed or not with the id mentioned in the url
        2. check the loogedin is ticket_created user or admin, If not returns a 404 page
        3. If successfull, then changing the ticket status

    """
    tickets = Ticket.objects.filter(id=ticket_id)
    if tickets:
        ticket = tickets[0]
        if request.user.is_staff or request.user == ticket.user:
            if request.POST.get("ticket_status"):
                ticket.status = request.POST.get("ticket_status")
                ticket.save()
                temp = loader.get_template("email/new_ticket.html")
                subject = "Your Ticket Status | Peeljobs"
                rendered = temp.render({"ticket": ticket, "status": True})
                mfrom = settings.DEFAULT_FROM_EMAIL
                user_active = True if ticket.user.is_active else False
                Memail(ticket.user.email, mfrom, subject, rendered, user_active)
                data = {
                    "error": False,
                    "response": "Ticket status changed Successfully",
                }
            else:
                data = {"error": True, "response": "Please select status"}
            return HttpResponse(json.dumps(data))
    message = "Sorry, No Ticket Found"
    reason = "The URL may be misspelled or the ticket you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )


@login_required
def ticket_comment(request, ticket_id):
    """
        1. Check for a ticket existed or not with the id mentioned in the url
        2. check the loogedin is ticket_created user or admin, If not returns a 404 page
        3. Then checking for form validations along with comment attachments
        4. If successfull, then comment will be created for a ticket
        5. A Notification email has been sent to the ticket_created user with the comment message

    """
    ticket = Ticket.objects.filter(id=ticket_id).first()
    if ticket:
        if request.user.is_staff or request.user == ticket.user:
            validate_comment = CommentForm(request.POST, request.FILES)
            if validate_comment.is_valid():
                comment = Comment.objects.create(
                    comment=request.POST.get("comment"),
                    ticket=ticket,
                    commented_by=request.user,
                )
                if request.FILES:
                    for key, value in request.FILES.items():
                        attachment = Attachment.objects.create(
                            attached_file=value, uploaded_by=request.user
                        )
                        comment.attachments.add(attachment)
                if request.user.is_superuser:
                    temp = loader.get_template("email/new_ticket.html")
                    subject = "Acknowledgement For Your Request | Peeljobs"
                    rendered = temp.render({"ticket": ticket, "comment": comment})
                    mfrom = settings.DEFAULT_FROM_EMAIL
                    user_active = True if ticket.user.is_active else False
                    Memail(ticket.user.email, mfrom, subject, rendered, user_active)
                return HttpResponse(
                    json.dumps(
                        {"error": False, "response": "Comment added Successfully"}
                    )
                )
            else:
                return HttpResponse(
                    json.dumps({"error": True, "response": validate_comment.errors})
                )
    reason = "The URL may be misspelled or the ticket you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": "404", "message": "Sorry, No Ticket Found", "reason": reason},
        status=404,
    )


@login_required
def edit_comment(request):
    """
        1. Check for a ticket existed or not with the id mentioned in the url
        2. check the loogedin user is comment_created user or admin, If not returns a 404 page
        3. Then checking for form validations along with comment attachments
        4. If successfull, then comment details will be updated for a ticket

    """

    comments = Comment.objects.filter(
        id=request.POST.get("comment_id"), commented_by=request.user
    )
    if comments:
        validate_comment = CommentForm(
            request.POST, request.FILES, instance=comments[0]
        )
        if validate_comment.is_valid():
            comment = validate_comment.save(commit=False)
            comment.commented_by = request.user
            comment.save()
            for key, value in request.FILES.items():
                attachment = Attachment.objects.create(
                    attached_file=value, uploaded_by=request.user
                )
                comment.attachments.add(attachment)
            data = {"error": False, "response": "Comment Updated Successfully"}
        else:
            errors = validate_comment.errors
            for key in request.POST.keys():
                if "attachment_" in key:
                    errors[key] = "This field is required"
            data = {"error": True, "response": errors}
    else:
        data = {
            "error": True,
            "response_message": "This comment can't edit by the User",
        }
    return HttpResponse(json.dumps(data))


@login_required
def admin_tickets_list(request):
    """
        Method: GET
            1. check the loogedin user is admin or not, If not returns a 404 page
            2. If user is amdin, then display a recent tickets to admin
            3. If successfull, then comment details will be updated for a ticket

    """

    if request.user.is_staff:
        tickets = Ticket.objects.filter().order_by("-created_on")
        return render(
            request, "dashboard/tickets/admin_ticket_list.html", {"tickets": tickets}
        )
    message = "Sorry, No Ticket Found"
    reason = "The URL may be misspelled or the ticket you're looking for is no longer available."
    return render(
        request,
        "404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )


TICKET_STATUS = (
    ("Open", "Open"),
    ("Closed", "Closed"),
    ("Ongoing", "Ongoing"),
)


@login_required
def admin_ticket_view(request, ticket_id):
    """
        Method: GET
            1. check the loogedin user is admin or not, If not returns a 404 page
            2. check ticket is existing or not with the id given in url
            3. If successfull, then display the ticket details to admin user

    """

    if request.user.is_staff:
        tickets = Ticket.objects.filter(id=ticket_id)
        if tickets:
            return render(
                request,
                "dashboard/tickets/ticket_view.html",
                {
                    "ticket": tickets[0],
                    "priorities": PRIORITY_TYPES,
                    "ticket_types": TICKET_TYPES,
                    "status": TICKET_STATUS,
                },
            )
    message = "Sorry, No Ticket Found"
    reason = "The URL may be misspelled or the ticket you're looking for is no longer available."
    return render(
        request,
        "404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )
