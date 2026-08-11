from django.urls import re_path as url

from tickets.views import (
    admin_ticket_view,
    admin_tickets_list,
    delete_attachment,
    delete_comment,
    delete_ticket,
    edit_comment,
    edit_ticket,
    index,
    new_ticket,
    ticket_comment,
    ticket_status,
    view_ticket,
)

app_name = "tickets"

urlpatterns = [
    url(r"^$", index, name="index"),
    url(
        r"ticket/edit/(?P<ticket_id>[a-zA-Z0-9_-]+)/$", edit_ticket, name="edit_ticket"
    ),
    url(
        r"ticket/view/(?P<ticket_id>[a-zA-Z0-9_-]+)/$", view_ticket, name="view_ticket"
    ),
    url(
        r"attachment/delete/(?P<attachment_id>[a-zA-Z0-9_-]+)/$",
        delete_attachment,
        name="delete_attachment",
    ),
    url(
        r"comment/delete/(?P<comment_id>[a-zA-Z0-9_-]+)/$",
        delete_comment,
        name="delete_comment",
    ),
    url(
        r"ticket/delete/(?P<ticket_id>[a-zA-Z0-9_-]+)/$",
        delete_ticket,
        name="delete_ticket",
    ),
    url(r"status/(?P<ticket_id>[a-zA-Z0-9_-]+)/$", ticket_status, name="ticket_status"),
    url(r"comment/edit/$", edit_comment, name="edit_comment"),
    url(
        r"comment/(?P<ticket_id>[a-zA-Z0-9_-]+)/$",
        ticket_comment,
        name="ticket_comment",
    ),
    url(r"ticket/list/$", admin_tickets_list, name="admin_tickets_list"),
    url(
        r"dashboard/ticket-view/(?P<ticket_id>[a-zA-Z0-9_-]+)/$",
        admin_ticket_view,
        name="admin_ticket_view",
    ),
    url(r"ticket/new/$", new_ticket, name="new_ticket"),
]
