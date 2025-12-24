from django import forms
from peeldb.models import Ticket, Comment


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "priority", "ticket_type"]


class CommentForm(forms.ModelForm):
    comment = forms.CharField(max_length=1000)

    class Meta:
        model = Comment
        fields = ["comment"]
