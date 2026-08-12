"""Agency forms, moved from recruiter/forms.py 2026-08-12 — agency/views.py
was their only consumer."""

from django import forms

from peeldb.models import AgencyCompany, AgencyWorkLog


class ClientForm(forms.ModelForm):
    logo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = AgencyCompany
        fields = ["name", "website", "decription"]

    def clean_name(self):
        companies = AgencyCompany.objects.filter(
            name=self.data["name"], website=self.data["website"]
        ).exclude(id=self.instance.id)
        if not companies:
            return self.data["name"]
        else:
            raise forms.ValidationError("Client with this name, website already exists")


class AgencyWorkLogForm(forms.ModelForm):
    class Meta:
        model = AgencyWorkLog
        fields = [
            "job_post",
            "user",
            "start_time",
            "end_time",
            "summary",
            "no_of_profiles",
        ]
