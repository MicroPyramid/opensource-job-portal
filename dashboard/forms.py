import re
from django import forms
from django.forms import ModelForm
from peeldb.models import (
    Country,
    MetaData,
    State,
    City,
    Skill,
    Language,
    Qualification,
    Industry,
    FunctionalArea,
    User,
    MailTemplate,
    Company,
    JobPost,
    Question,
)


def validation_name(self, model):
    form_cleaned_data = self.cleaned_data
    if model == "Country":
        if Country.objects.filter(name__iexact=form_cleaned_data["name"]).exclude(
            id=self.instance.id
        ):
            raise forms.ValidationError(model + " name Should be unique")

    if model == "State":
        if State.objects.filter(name__iexact=form_cleaned_data["name"]).exclude(
            id=self.instance.id
        ):
            raise forms.ValidationError(model + " name Should be unique")
    if model == "City":
        if City.objects.filter(name__iexact=form_cleaned_data["name"]).exclude(
            id=self.instance.id
        ):
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
        fields = ["name", "state", "slug"]

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

        # if bool(re.search(r"[0-9]", form_cleaned_data['name'])):
        #     raise forms.ValidationError("Qualification name Should not contain numbers")
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

    def clean_mobile(self):
        if self.data["mobile"]:
            if len(self.data["mobile"]) < 10 or len(self.data["mobile"]) > 12:
                raise forms.ValidationError("Please Enter Valid phone number")
            else:
                return self.data["mobile"]

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
        super(MailTemplateForm, self).__init__(*args, **kwargs)
        if "mode" in self.data.keys() and self.data["mode"] == "send_mail":
            self.fields["recruiters"].required = True
        if "show_recruiter" in self.data.keys() and self.data["show_recruiter"] == "on":
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
        if (
            "show_recruiter" in self.data.keys()
            and str(self.data["show_recruiter"]) == "True"
        ):
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
        instance = super(CompanyForm, self).save(commit=False)
        instance.name = self.cleaned_data["name"]
        if "website" in self.cleaned_data.keys():
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


class QuestionForm(ModelForm):
    answer = forms.CharField(required=False)
    status = forms.CharField(required=False)

    class Meta:
        model = Question
        fields = ["title", "description", "skills", "created_by", "status"]

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if not self.data.get("form-TOTAL_FORMS"):
            self.fields["status"].required = True

    def clean_answer(self):
        if self.data.get("form-TOTAL_FORMS"):
            num = int(self.data.get("form-TOTAL_FORMS"))
            for i in range(0, num):
                answers = self.data.getlist("form-" + str(i) + "-answer")
                if "" in answers:
                    raise forms.ValidationError("Answer field Required")


class SolutionForm(ModelForm):
    answer = forms.CharField(required=True)

    class Meta:
        model = Question
        fields = ["status"]


class MetaForm(ModelForm):
    class Meta:
        model = MetaData
        fields = ["name", "meta_title", "meta_description", "h1_tag"]
