import re
from django import forms
from peeldb.models import simplecontact, Subscriber, User


class SimpleContactForm(forms.ModelForm):
    class Meta:
        model = simplecontact
        fields = [
            "first_name",
            "last_name",
            "comment",
            "email",
            "enquery_type",
            "phone",
        ]


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email", "skill"]

    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)
        if "subscribe_from" in self.data.keys():
            self.fields["skill"].required = False


class UserEmailRegisterForm(forms.ModelForm):
    mobile = forms.CharField(
        required=True,
        error_messages={
            "required": "Phone Number can not be blank",
            "invalid": "Please enter a valid phone number",
        },
    )
    year = forms.IntegerField(required=False)
    month = forms.CharField(required=False)
    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "Email can not be blank",
            "invalid": "Please enter a valid email",
        },
    )
    password = forms.CharField(
        required=True, error_messages={"required": "Password can not be blank"}
    )
    resume = forms.FileField(required=False)
    other_location = forms.CharField(
        required=False, error_messages={"required": "Other Location cannot be empty"}
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "mobile",
            "technical_skills",
            "current_city",
            "year",
            "month",
            "resume",
        ]

    def __init__(self, *args, **kwargs):
        super(UserEmailRegisterForm, self).__init__(*args, **kwargs)
        self.fields["current_city"].required = True
        self.fields["current_city"].error_messages = {
            "required": "Current Location cannot be empty"
        }
        self.fields["technical_skills"].error_messages = {
            "required": "Skills cannot be empty"
        }
        if "social" in self.data.keys():
            self.fields.pop("password")
            self.fields["email"].required = False
        if "other_loc" in self.data.keys():
            self.fields["current_city"].required = False
            self.fields["other_location"].required = True

    def clean_email(self):
        form_cleaned_data = self.cleaned_data
        user = User.objects.filter(email__iexact=form_cleaned_data["email"]).exclude(
            id=self.instance.id
        )
        if user.exists():
            raise forms.ValidationError(
                "User Already Exists as " + user[0].get_user_type_display()
            )
        return form_cleaned_data["email"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) < 7:
            raise forms.ValidationError(
                "The password must be at least %d characters long." % 7
            )
        return password

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if mobile:
            users = User.objects.filter(mobile=mobile).exclude(id=self.instance.id)
            if not users:
                length = len(str(mobile)) < 10 or len(str(mobile)) > 12
                symbols = bool(
                    re.search(r"[~\.,!@#\$%\^&\*\(\)_\{}\":;'\[\]]", mobile)
                ) or bool(re.search("[a-zA-Z]", mobile))
                if length or symbols:
                    raise forms.ValidationError("Please Enter Valid phone number")
                else:
                    return mobile
            else:
                raise forms.ValidationError(
                    "User with this mobile number already exists"
                )

    def clean_resume(self):
        if self.cleaned_data["resume"]:
            fo = self.cleaned_data.get("resume")
            if not isinstance(fo, str):
                sup_formates = [
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "application/pdf",
                    "application/rtf",
                    "application/x-rtf",
                    "text/richtext",
                    "application/msword",
                    "application/vnd.oasis.opendocument.text",
                    "application/x-vnd.oasis.opendocument.text",
                ]
                ftype = fo.content_type
                size = fo.size / 1024
                if str(ftype) in sup_formates:
                    if size < 300 and size > 0:
                        return fo
                    else:
                        raise forms.ValidationError(
                            "File Size must be less than 300 kb"
                        )
                else:
                    raise forms.ValidationError(
                        "Upload valid format files EX: Doc, Docx, Pdf"
                    )


class AuthenticationForm(forms.Form):
    email = forms.EmailField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        username = self.cleaned_data.get("email")
        user = User.objects.filter(email=username).first()
        if user:
            if not user.is_jobseeker:
                raise forms.ValidationError(
                    "You have registered as "
                    + user.get_user_type_display()
                    + " and you can't login as Job Seeker"
                )
            return username
        else:
            raise forms.ValidationError("User not found with this email")


class UserPassChangeForm(forms.Form):
    new_password = forms.CharField(max_length=50)
    retype_password = forms.CharField(max_length=50)

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        if password and len(password) < 7:
            raise forms.ValidationError(
                "The password must be at least %d characters long." % 7
            )
        return password


class ForgotPassForm(forms.Form):
    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "Email can not be blank",
            "invalid": "Please enter a valid email",
        },
    )
