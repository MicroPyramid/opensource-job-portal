"""Applicant status form, moved from recruiter/forms.py 2026-08-12.

Rendered by peeldb/templatetags/page_tags.py, which is why it lives here
rather than in an app that is on its way out."""

from django import forms

APPLICANT_STATUS_CHOICES = [
    ("Process", "Process"),
    ("Pending", "Pending"),
    ("Selected", "Selected"),
    ("Shortlisted", "Shortlisted"),
    ("Rejected", "Rejected"),
]


class UserStatus(forms.Form):
    status = forms.ChoiceField(choices=APPLICANT_STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        if user.user:
            user_id = user.user.id
        else:
            user_id = user.resume_applicant.id
        super().__init__(*args, **kwargs)
        self.fields["status"].initial = user.status
        self.fields["status"].widget.attrs.update(
            {"id": "user_status_" + str(user_id), "class": "user_status"}
        )
