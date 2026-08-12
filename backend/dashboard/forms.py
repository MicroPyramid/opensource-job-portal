import re
from datetime import datetime

from django import forms
from django.forms import ModelForm

from mpcomp.views import get_asia_time
from peeldb.models import (
    City,
    Company,
    Country,
    FunctionalArea,
    Industry,
    JobPost,
    Language,
    MailTemplate,
    Menu,
    MetaData,
    Qualification,
    Skill,
    State,
    User,
)


def validation_name(self, model):
    form_cleaned_data = self.cleaned_data
    if model == "Country" and Country.objects.filter(
        name__iexact=form_cleaned_data["name"]
    ).exclude(id=self.instance.id):
        raise forms.ValidationError(model + " name Should be unique")

    if model == "State" and State.objects.filter(
        name__iexact=form_cleaned_data["name"]
    ).exclude(id=self.instance.id):
        raise forms.ValidationError(model + " name Should be unique")
    if model == "City" and City.objects.filter(
        name__iexact=form_cleaned_data["name"]
    ).exclude(id=self.instance.id):
        raise forms.ValidationError(model + " name Should be unique")

    if bool(
        re.search(r"[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]", form_cleaned_data["name"])
    ) or bool(re.search(r"[0-9]", form_cleaned_data["name"])):
        raise forms.ValidationError(
            model + " name Should not contain special charecters and numbers"
        )
    return form_cleaned_data["name"]


class ChangePasswordForm(forms.Form):
    oldpassword = forms.CharField(max_length=50)
    newpassword = forms.CharField(max_length=50)
    retypepassword = forms.CharField(max_length=50)


class CountryForm(ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = Country
        fields = ["name", "slug"]

    def clean_name(self):
        return validation_name(self, "Country")

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "")
        if slug and Country.objects.filter(slug=slug).exclude(id=self.instance.id):
            raise forms.ValidationError("Slug name Should be unique")
        return slug or self.instance.slug


class StateForm(ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = State
        fields = ["name", "country", "slug"]

    def clean_name(self):
        return validation_name(self, "State")

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "")
        if slug and State.objects.filter(slug=slug).exclude(id=self.instance.id):
            raise forms.ValidationError("Slug name Should be unique")
        return slug or self.instance.slug


class CityForm(ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = City
        fields = ["name", "state", "slug", "status"]

    def clean_name(self):
        return validation_name(self, "City")

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "")
        if slug and City.objects.filter(slug=slug).exclude(id=self.instance.id):
            raise forms.ValidationError("Slug name Should be unique")
        return slug or self.instance.slug


class SkillForm(ModelForm):
    slug = forms.SlugField(required=False)
    icon = forms.ImageField(required=False)

    class Meta:
        model = Skill
        fields = ["name", "slug"]

    def clean_name(self):
        form_cleaned_data = self.cleaned_data
        if Skill.objects.filter(name__iexact=form_cleaned_data["name"]).exclude(
            id=self.instance.id
        ):
            raise forms.ValidationError("Skill name Should be unique")
        return form_cleaned_data["name"]

    def clean_slug(self):
        form_cleaned_data = self.cleaned_data
        if Skill.objects.filter(name__iexact=form_cleaned_data["slug"]).exclude(
            id=self.instance.id
        ):
            raise forms.ValidationError("Skill slug Should be unique")
        return form_cleaned_data["slug"]

    def clean_icon(self):
        icon = self.cleaned_data.get("icon")
        if icon:
            sup_formates = ["image/jpeg", "image/png"]
            ftype = icon.content_type
            if str(ftype) not in sup_formates:
                raise forms.ValidationError(
                    "Please upload Valid Image Format Ex: PNG, JPEG, JPG"
                )
            return icon
        return icon


class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = ["name"]

    def clean_name(self):
        form_cleaned_data = self.cleaned_data

        if Language.objects.filter(name=form_cleaned_data["name"]).exists():
            raise forms.ValidationError("Language name Should be unique")

        if bool(
            re.search(r"[~\!@#\$%\^&\*\(\)_\+{}\":;,.'\[\]]", form_cleaned_data["name"])
        ) or bool(re.search(r"[0-9]", form_cleaned_data["name"])):
            raise forms.ValidationError("Language name Should not contain numbers")
        return form_cleaned_data["name"]


class QualificationForm(ModelForm):
    class Meta:
        model = Qualification
        fields = ["name"]

    def clean_name(self):
        form_cleaned_data = self.cleaned_data

        if Qualification.objects.filter(name=form_cleaned_data["name"]).exists():
            raise forms.ValidationError("Qualification name Should be unique")
        return form_cleaned_data["name"]


class IndustryForm(ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = Industry
        fields = ["name", "slug"]

    def clean_name(self):
        form_cleaned_data = self.cleaned_data

        if Industry.objects.filter(name=form_cleaned_data["name"]).exclude(
            id=self.instance.id
        ):
            raise forms.ValidationError("Industry name Should be unique")

        if bool(re.search(r"[0-9]", form_cleaned_data["name"])):
            raise forms.ValidationError("Industry name Should not contain numbers")
        return form_cleaned_data["name"]

    def clean_slug(self):
        form_cleaned_data = self.cleaned_data
        if Industry.objects.filter(slug=form_cleaned_data["slug"]).exclude(
            id=self.instance.id
        ):
            raise forms.ValidationError("Slug name Should be unique")
        return form_cleaned_data["slug"]


class UserForm(ModelForm):
    profile_pic = forms.ImageField(required=False)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    user_type = forms.CharField(max_length=30)
    # password = forms.CharField(max_length=30)
    mobile = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "address",
            "permanent_address",
            "mobile",
            "gender",
        ]

    # def clean_password(self):
    #     if self.instance.id:
    #         return ''
    #     else:
    #         if len(self.data['password']) < 4 or len(self.data['password']) > 15:
    #             raise forms.ValidationError(
    #                 'password must contain atleast 4 to 15 Characters')
    #         else:
    #             return self.data['password']


class FunctionalAreaForm(ModelForm):
    class Meta:
        model = FunctionalArea
        fields = ["name"]

    def clean_name(self):
        form_cleaned_data = self.cleaned_data

        if bool(re.search(r"[0-9]", form_cleaned_data["name"])):
            raise forms.ValidationError(
                "FunctionalArea name Should not contain numbers"
            )
        return form_cleaned_data["name"]


class MailTemplateForm(ModelForm):
    recruiters = forms.CharField(max_length=1000, required=False)
    applicant_status = forms.CharField(max_length=1000, required=False)

    class Meta:
        model = MailTemplate
        fields = ["subject", "message", "title", "show_recruiter"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "mode" in self.data and self.data["mode"] == "send_mail":
            self.fields["recruiters"].required = True
        if "show_recruiter" in self.data and self.data["show_recruiter"] == "on":
            self.fields["applicant_status"].required = True

    def clean_subject(self):
        if len(self.data["subject"]) > 100:
            raise forms.ValidationError(
                "Subject is too long, we expect it to be less than 100 characters"
            )
        else:
            return self.data["subject"]

    def clean_message(self):
        if len(self.data["message"]) > 200000:
            raise forms.ValidationError(
                "Mail is too big, please try with simple matter!"
            )
        else:
            return self.data["message"]

    def clean_show_recruiter(self):
        if "show_recruiter" in self.data and str(self.data["show_recruiter"]) == "True":
            if MailTemplate.objects.filter(
                applicant_status=self.data["applicant_status"], show_recruiter=True
            ).exclude(id=self.instance.id):
                raise forms.ValidationError(
                    "Mail Template with this status already exists!"
                )
            return self.data["show_recruiter"]


class CompanyForm(ModelForm):
    profile_pic = forms.ImageField(required=False)
    campaign_icon = forms.ImageField(required=False)

    class Meta:
        model = Company
        fields = ["name", "address", "profile", "website"]

    def clean_name(self):
        companies = Company.objects.filter(name=self.data["name"]).exclude(
            id=self.instance.id
        )
        if companies:
            raise forms.ValidationError("Company with this name already exists")
        return self.data["name"]

    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get("profile_pic")
        if profile_pic:
            sup_formates = ["image/jpeg", "image/png"]
            ftype = profile_pic.content_type
            if str(ftype) not in sup_formates:
                raise forms.ValidationError(
                    "Please upload Valid Image Format Ex: PNG, JPEG, JPG"
                )
            return profile_pic
        return profile_pic

    def clean_campaign_icon(self):
        campaign_icon = self.cleaned_data.get("campaign_icon")
        if campaign_icon:
            sup_formates = ["image/jpeg", "image/png"]
            ftype = campaign_icon.content_type
            if str(ftype) not in sup_formates:
                raise forms.ValidationError(
                    "Please upload Valid Image Format Ex: PNG, JPEG, JPG"
                )
            return campaign_icon
        return campaign_icon

    def clean_website(self):
        if self.cleaned_data["website"]:
            if (
                re.match(r"^http://", self.cleaned_data["website"])
                or re.match(r"^https://", self.cleaned_data["website"])
                or re.match(r"^www.", self.cleaned_data["website"])
            ):
                companies = Company.objects.filter(
                    website=self.data["website"]
                ).exclude(id=self.instance.id)
                if companies:
                    raise forms.ValidationError(
                        "Company with this website already exists"
                    )
                return self.cleaned_data["website"]
            else:
                raise forms.ValidationError(
                    "Please include website with http:// or https:// or www."
                )
        return self.cleaned_data["website"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.name = self.cleaned_data["name"]
        if "website" in self.cleaned_data:
            instance.website = self.cleaned_data["website"]
        else:
            instance.website = None
        instance.address = self.cleaned_data["address"]
        instance.profile = self.cleaned_data["profile"]
        if not self.instance:
            instance.company_type = "Company"
        if commit:
            instance.save()
        return instance


class JobPostTitleForm(ModelForm):
    pincode = forms.CharField(required=False)

    class Meta:
        model = JobPost
        fields = ["title", "description"]

    def clean_title(self):
        if bool(
            re.search(
                r"[~\.,!@#\$%\^&\*\(\)_\+{}\":;'\[\]\<\>\|\/]",
                self.cleaned_data["title"],
            )
        ):
            raise forms.ValidationError(
                "Title Should not contain special characters and numbers"
            )
        if JobPost.objects.filter(title=self.cleaned_data["title"]).exclude(
            id=self.instance.id
        ):
            raise forms.ValidationError("Job Post with this title already exists")
        return self.cleaned_data["title"]

    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode")
        if pincode:
            match = re.findall(r"\d{6}", pincode)
            if not match or len(pincode) != 6:
                raise forms.ValidationError("Please enter 6 digit valid Pincode")
        return pincode


class MetaForm(ModelForm):
    class Meta:
        model = MetaData
        fields = ["name", "meta_title", "meta_description", "h1_tag"]


# Moved from recruiter/forms.py 2026-08-12. Only dashboard used them, and
# the import was the last thing keeping the legacy recruiter app in the graph.
valid_time_formats = ["%H:%M", "%I:%M%p", "%I:%M %p"]


class JobPostForm(ModelForm):
    min_salary = forms.IntegerField(required=False)
    max_salary = forms.IntegerField(required=False)
    published_date = forms.DateTimeField(
        input_formats=("%m/%d/%Y %H:%M:%S",), required=False
    )
    walkin_contactinfo = forms.CharField(max_length=10000, required=False)
    walkin_from_date = forms.DateField(required=False, input_formats=("%m/%d/%Y",))
    walkin_to_date = forms.DateField(required=False, input_formats=("%m/%d/%Y",))
    walkin_time = forms.TimeField(required=False, input_formats=valid_time_formats)
    vacancies = forms.IntegerField(required=False)
    company_description = forms.CharField(max_length=10000)
    application_fee = forms.IntegerField(required=False)
    selection_process = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Please enter the  selection process"}
        ),
        required=False,
    )
    how_to_apply = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Please enter the  selection process"}
        ),
        required=False,
    )
    important_dates = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Please enter the  selection process"}
        ),
        required=False,
    )
    govt_from_date = forms.DateField(required=False, input_formats=("%m/%d/%Y",))
    govt_to_date = forms.DateField(required=False, input_formats=("%m/%d/%Y",))
    govt_exam_date = forms.DateField(required=False, input_formats=("%m/%d/%Y",))
    age_relaxation = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Please enter the  selection process"}
        ),
        required=False,
    )
    min_year = forms.IntegerField(required=True)
    max_year = forms.IntegerField(required=True)
    min_month = forms.IntegerField(required=True)
    max_month = forms.IntegerField(required=True)
    company_address = forms.CharField(max_length=10000)
    agency_job_type = forms.CharField(max_length=10000, required=False)
    agency_invoice_type = forms.CharField(max_length=10000, required=False)
    agency_amount = forms.IntegerField(required=False)
    # agency_recruiters = forms.CharField(max_length=10000, required=False)
    agency_client = forms.CharField(max_length=10000, required=False)
    agency_category = forms.CharField(max_length=10000, required=False)
    company = forms.CharField(max_length=100, required=False)
    # edu_qualification = forms.CharField(max_length=1000, required=False)
    company_links = forms.CharField(max_length=5000, required=False)
    salary_type = forms.CharField(required=False)
    published_message = forms.CharField(required=False)
    company_website = forms.CharField(max_length=5000, required=False)
    company_logo = forms.ImageField(required=False)
    pincode = forms.CharField(required=False)

    class Meta:
        model = JobPost
        exclude = [
            "user",
            "code",
            "country",
            "status",
            "previous_status",
            "fb_views",
            "tw_views",
            "ln_views",
            "other_views",
            "fb_groups",
            "post_on_fb",
            "post_on_tw",
            "post_on_ln",
            "keywords",
            "job_interview_location",
            "job_type",
            "govt_job_type",
            "agency_client",
            "company",
            "meta_title",
            "meta_description",
            "agency_category",
            "major_skill",
            "vacancies",
            "slug",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user.is_superuser:
            self.fields["company"].required = True
            self.fields["company_address"].required = False
            self.fields["company_name"].required = False
            self.fields["company_description"].required = False
            self.fields["company_website"].required = False

        if self.user.company and self.user.is_agency_recruiter:
            # self.fields['code'].required = False
            self.fields["agency_job_type"].required = True
            self.fields["agency_recruiters"].required = True
        else:
            self.fields["agency_recruiters"].required = False

        if self.data.get("vacancies"):
            self.fields["vacancies"].required = True

        if self.data.get("salary_type"):
            self.fields["max_salary"].required = True
            self.fields["min_salary"].required = True

        if self.data.get("min_salary") or self.data.get("max_salary"):
            self.fields["salary_type"].required = True

        if self.data.get("min_salary"):
            self.fields["salary_type"].required = True
            self.fields["min_salary"].required = True
        if self.data.get("max_salary"):
            self.fields["max_salary"].required = True
            self.fields["salary_type"].required = True

        if "final_industry" in self.data:
            if len(self.data["final_industry"]) > 2:
                self.fields["industry"].required = False
            else:
                self.fields["industry"].required = True
        if "final_skills" in self.data:
            if len(self.data["final_skills"]) > 2:
                self.fields["skills"].required = False
            else:
                self.fields["skills"].required = True
        if "final_edu_qualification" in self.data:
            if len(self.data["final_edu_qualification"]) > 2:
                self.fields["edu_qualification"].required = False
            else:
                self.fields["edu_qualification"].required = True
        if "other_location" in self.data and len(self.data["other_location"]) != 0:
            self.fields["location"].required = False

        if self.data.get("visa_required"):
            self.fields["visa_country"].required = True
            self.fields["visa_type"].required = True
        else:
            self.fields["visa_country"].required = False
            self.fields["visa_type"].required = False

        if str(self.data["job_type"]) == "walk-in":
            self.fields["walkin_contactinfo"].required = True
            self.fields["walkin_from_date"].required = True
            self.fields["walkin_to_date"].required = True
            self.fields["walkin_time"].required = True
            self.fields["vacancies"].required = False
            # self.fields['company_description'].required = False
            self.fields["industry"].required = False
            self.fields["skills"].required = False
            # self.fields['code'].required = False
            self.fields["job_role"].required = False
            self.fields["company_description"].required = False
            self.fields["walkin_time"].required = False
            self.fields["edu_qualification"].required = False

        if str(self.data["job_type"]) == "government":
            self.fields["min_year"].required = False
            self.fields["max_year"].required = False
            self.fields["min_month"].required = False
            self.fields["max_month"].required = False
            self.fields["company_address"].required = False

            self.fields["application_fee"].required = False
            self.fields["selection_process"].required = False
            self.fields["how_to_apply"].required = True
            self.fields["important_dates"].required = True
            self.fields["age_relaxation"].required = True
            self.fields["govt_from_date"].required = True
            self.fields["govt_to_date"].required = True
            self.fields["govt_exam_date"].required = False

            self.fields["industry"].required = False
            self.fields["skills"].required = False
            # self.fields['code'].required = False
            self.fields["job_role"].required = False
            self.fields["company_description"].required = False

        if str(self.data["job_type"]) == "full-time":
            self.fields["edu_qualification"].required = False

        if str(self.data["job_type"]) == "internship":
            self.fields["edu_qualification"].required = False

    def clean_title(self):
        title = self.cleaned_data["title"]
        if bool(
            re.search(r"[~\.,!@#\$%\^&\*\(\)_\+{}\":;'\[\]\<\>\|\/]", title)
        ) or bool(re.search(r"[0-9]", title)):
            raise forms.ValidationError(
                "Title Should not contain special charecters and numbers"
            )
        if JobPost.objects.filter(title=title).exclude(id=self.instance.id):
            raise forms.ValidationError("Job Post with this title already exists")
        return title.replace("/", "-")

    def clean_vacancies(self):
        if self.data.get("vacancies"):
            if int(self.data["vacancies"]) <= 0:
                raise forms.ValidationError("Vacancies must be greater than zero")
            else:
                return self.cleaned_data.get("vacancies")
        return self.cleaned_data.get("vacancies")

    def clean_govt_exam_date(self):
        if ("govt_exam_date", "govt_from_date", "govt_to_date") in self.data:
            date = self.cleaned_data["govt_exam_date"]
            from_date = self.data["govt_from_date"]
            to_date = self.data["govt_to_date"]
            if date and from_date and to_date:
                to_date = datetime.strptime(str(to_date), "%m/%d/%Y").strftime(
                    "%Y-%m-%d"
                )
                from_date = datetime.strptime(str(from_date), "%m/%d/%Y").strftime(
                    "%Y-%m-%d"
                )

                if str(date) < str(datetime.now().date()):
                    raise forms.ValidationError("The date cannot be in the past!")
                if str(from_date) > str(date) or str(to_date) > str(date):
                    raise forms.ValidationError(
                        "Exam Date must be in between from and to date"
                    )
                return date

    def clean_govt_from_date(self):
        if "govt_from_date" in self.data:
            date = self.cleaned_data["govt_from_date"]
            if str(date) < str(datetime.now().date()):
                raise forms.ValidationError("The date cannot be in the past!")
            return date

    def clean_govt_to_date(self):
        if "govt_to_date" in self.data:
            date = self.cleaned_data["govt_to_date"]
            if str(date) < str(datetime.now().date()):
                raise forms.ValidationError("The date cannot be in the past!")
            from_date = self.data["govt_from_date"]
            from_date = datetime.strptime(str(from_date), "%m/%d/%Y").strftime(
                "%Y-%m-%d"
            )
            if str(from_date) > str(date):
                raise forms.ValidationError("To Date must be greater than From Date")
            return date

    def clean_published_date(self):
        date_time = self.cleaned_data["published_date"]
        asia_time = get_asia_time()
        if date_time:
            if str(date_time) < str(asia_time):
                raise forms.ValidationError("The date cannot be in the past!")
            if str(self.data["job_type"]) == "walk-in":
                if (
                    "walkin_to_date" in self.cleaned_data
                    and self.cleaned_data["walkin_to_date"] > date_time.date()
                ):
                    return date_time
                else:
                    raise forms.ValidationError(
                        "Published date must be less than walkin end date"
                    )
            return date_time

    def clean_min_salary(self):
        if self.cleaned_data.get("min_salary"):
            try:
                min_sal = int(self.cleaned_data["min_salary"])
                return min_sal
            except Exception:
                raise forms.ValidationError("Minimum salary must be an Integer")
        else:
            return 0

    def clean_max_salary(self):
        if self.cleaned_data.get("min_salary") and self.cleaned_data.get("max_salary"):
            if int(self.cleaned_data["max_salary"]) < int(
                self.cleaned_data["min_salary"]
            ):
                raise forms.ValidationError(
                    "Maximum salary must be greater than minimum salary"
                )
            return self.cleaned_data["max_salary"]
        elif self.cleaned_data.get("max_salary"):
            return self.cleaned_data["max_salary"]
        return 0

    def clean_company_name(self):
        # companies = Company.objects.filter(name__iexact=self.data['company_name'])
        # if self.instance.company:
        #     companies = companies.exclude(id=self.instance.company.id)
        # if companies:
        #     raise forms.ValidationError('Company with this name already exists')
        return self.data["company_name"]

    def clean_company_website(self):
        if self.data.get("company_website"):
            if (
                re.match(r"^http://", self.data["company_website"])
                or re.match(r"^https://", self.data["company_website"])
                or re.match(r"^www.", self.data["company_website"])
            ):
                company = ""
                if self.data.get("company_id"):
                    company = Company.objects.filter(id=self.data["company_id"])
                if company:
                    companies = Company.objects.filter(
                        website__iexact=self.data["company_website"]
                    ).exclude(id=self.data["company_id"])
                    if companies:
                        raise forms.ValidationError(
                            "Company with this website already exists"
                        )
                return self.cleaned_data["company_website"]
            else:
                raise forms.ValidationError(
                    "Please include website with http:// or https:// or www."
                )

    def clean_company_logo(self):
        company_logo = self.cleaned_data.get("company_logo")
        if company_logo:
            sup_formates = ["image/jpeg", "image/png"]
            ftype = company_logo.content_type
            if str(ftype) not in sup_formates:
                raise forms.ValidationError(
                    "Please upload Valid Image Format Ex: PNG, JPEG, JPG"
                )
            return company_logo
        return company_logo

    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode")
        if pincode:
            match = re.findall(r"\d{6}", pincode)
            if not match or len(pincode) != 6:
                raise forms.ValidationError("Please Enter 6 digit valid Pincode")
        return pincode


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ["title", "url"]
