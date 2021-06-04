import re
from datetime import datetime, date
from rest_framework import serializers
from peeldb.models import (
    JobPost,
    Company,
    Country,
    Skill,
    FunctionalArea,
    Industry,
    Qualification,
    City,
    User,
    AgencyCompany,
    State,
    Menu,
)
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate
from mpcomp.views import get_asia_time, custom_password_check


valid_time_formats = ["%H:%M", "%I:%M%p", "%I:%M %p"]


class UserSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    def get_company(self, obj):
        return CompanySerializer(obj.company).data

    class Meta:
        model = User
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LoginSerializer, self).__init__(*args, **kwargs)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user:
                if not self.user.is_active:
                    if not self.user.is_active:
                        raise serializers.ValidationError(
                            "Your Account is inactive please contact admin."
                        )
                    else:
                        today_date = date.today()
                        user_created_date = self.user.created_on
                        difference = today_date - user_created_date
                        if difference.days > 7:
                            raise serializers.ValidationError(
                                "Please activate your account by verifying your email."
                            )
                if not (self.user.is_agency_recruiter or self.user.is_recruiter):
                    raise serializers.ValidationError("You are not recuiter")
            else:
                raise serializers.ValidationError("Invalid email and password")
        return data


class JobPostSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()

    def get_skills(self, obj):
        return SkillSerializer(obj.skills.all(), many=True).data

    def get_location(self, obj):
        return CitySerializer(obj.location.all(), many=True).data

    def get_industry(self, obj):
        return IndustrySerializer(obj.industry.all(), many=True).data

    class Meta:
        model = JobPost
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class FunctionalAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionalArea
        fields = "__all__"


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = "__all__"


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class AgencyCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyCompany
        fields = "__all__"


class CreateJobPostSerailizer(serializers.ModelSerializer):
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
        super(CreateJobPostSerailizer, self).__init__(*args, **kwargs)

        if self.user.is_superuser:
            self.fields["company"].required = True
            self.fields["company_address"].required = False
            self.fields["company_name"].required = False
            self.fields["company_description"].required = False
            self.fields["company_website"].required = False

        if self.user.company and self.user.is_agency_recruiter:
            self.fields["agency_job_type"].required = True
            self.fields["agency_recruiters"].required = True
        else:
            self.fields["agency_recruiters"].required = False

        # if "vacancies" in self.data.keys() and self.data["vacancies"]:
        #     self.fields["vacancies"].required = True

        if "salary_type" in kwargs["data"].keys() and kwargs["data"]["salary_type"]:
            self.fields["max_salary"].required = True
            self.fields["min_salary"].required = True

        if (
            "min_salary" in kwargs["data"].keys()
            and kwargs["data"]["min_salary"]
            or "max_salary" in kwargs["data"].keys()
            and kwargs["data"]["max_salary"]
        ):
            self.fields["salary_type"].required = True

        if "min_salary" in kwargs["data"].keys() and kwargs["data"]["min_salary"]:
            self.fields["salary_type"].required = True
            self.fields["min_salary"].required = True
        if "max_salary" in kwargs["data"].keys() and kwargs["data"]["max_salary"]:

            self.fields["max_salary"].required = True
            self.fields["salary_type"].required = True

        if "final_industry" in kwargs["data"].keys():
            if len(kwargs["data"]["final_industry"]) > 2:
                self.fields["industry"].required = False
            else:
                self.fields["industry"].required = True
        if "final_skills" in kwargs["data"].keys():
            if len(kwargs["data"]["final_skills"]) > 2:
                self.fields["skills"].required = False
            else:
                self.fields["skills"].required = True
        if "final_edu_qualification" in kwargs["data"].keys():
            if len(kwargs["data"]["final_edu_qualification"]) > 2:
                self.fields["edu_qualification"].required = False
            else:
                self.fields["edu_qualification"].required = True
        if "final_functional_area" in kwargs["data"].keys():
            if len(kwargs["data"]["final_functional_area"]) > 2:
                self.fields["functional_area"].required = False
            else:
                self.fields["functional_area"].required = True
        if "other_location" in kwargs["data"].keys():
            if len(kwargs["data"]["other_location"]) != 0:
                self.fields["location"].required = False

        if "visa_required" in kwargs["data"].keys() and kwargs["data"]["visa_required"]:
            self.fields["visa_country"].required = True
            self.fields["visa_type"].required = True
        else:
            self.fields["visa_country"].required = False
            self.fields["visa_type"].required = False

        if str(kwargs["data"]["job_type"]) == "walk-in":
            self.fields["walkin_contactinfo"].required = True
            self.fields["walkin_from_date"].required = True
            self.fields["walkin_to_date"].required = True
            self.fields["walkin_time"].required = True
            self.fields["vacancies"].required = False
            # self.fields['company_description'].required = False
            self.fields["industry"].required = False
            self.fields["skills"].required = False
            self.fields["functional_area"].required = False
            self.fields["last_date"].required = False
            # self.fields['code'].required = False
            self.fields["job_role"].required = False
            self.fields["company_description"].required = False
            self.fields["walkin_time"].required = False
            self.fields["edu_qualification"].required = False

        if str(kwargs["data"]["job_type"]) == "government":

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
            self.fields["functional_area"].required = False
            self.fields["last_date"].required = False
            self.fields["job_role"].required = False
            self.fields["company_description"].required = False

        if str(kwargs["data"]["job_type"]) in ["internship", "full-time"]:
            self.fields["last_date"].required = False
            self.fields["edu_qualification"].required = False

    def validate_title(self, title):
        if bool(
            re.search(r"[~\.,!@#\$%\^&\*\(\)_\+{}\":;'\[\]\<\>\|\/]", title)
        ) or bool(re.search(r"[0-9]", title)):
            raise serializers.ValidationError(
                "Title Should not contain special charecters and numbers"
            )
        if JobPost.objects.filter(title__iexact=title):
            raise serializers.ValidationError("Job Post with this title already exists")
        return title.replace("/", "-")

    def validate_vacancies(self, vacancies):
        if "vacancies" in self.data.keys() and self.data["vacancies"]:
            if int(vacancies) <= 0:
                raise serializers.ValidationError("Vacancies must be greater than zero")
            else:
                return self.cleaned_data.get("vacancies")
        return self.cleaned_data.get("vacancies")

    def validate_last_date(self):
        date = self.cleaned_data["last_date"]
        if str(date) < str(datetime.now().date()):
            raise serializers.ValidationError("The date cannot be in the past!")
        return date

    def validate_govt_exam_date(self):
        if ("govt_exam_date", "govt_from_date", "govt_to_date") in self.data.keys():
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
                    raise serializers.ValidationError("The date cannot be in the past!")
                if str(from_date) > str(date) or str(to_date) > str(date):
                    raise serializers.ValidationError(
                        "Exam Date must be in between from and to date"
                    )
                return date

    def validate_govt_from_date(self):
        if "govt_from_date" in self.data.keys():
            date = self.cleaned_data["govt_from_date"]
            if str(date) < str(datetime.now().date()):
                raise serializers.ValidationError("The date cannot be in the past!")
            return date

    def validate_govt_to_date(self):
        if "govt_to_date" in self.data.keys():
            date = self.cleaned_data["govt_to_date"]
            if str(date) < str(datetime.now().date()):
                raise serializers.ValidationError("The date cannot be in the past!")
            from_date = self.data["govt_from_date"]
            from_date = datetime.strptime(str(from_date), "%m/%d/%Y").strftime(
                "%Y-%m-%d"
            )
            if str(from_date) > str(date):
                raise serializers.ValidationError(
                    "To Date must be greater than From Date"
                )
            return date

    def validate_published_date(self):
        date_time = self.cleaned_data["published_date"]
        asia_time = get_asia_time()
        if date_time:
            if str(date_time) < str(asia_time):
                raise serializers.ValidationError("The date cannot be in the past!")
            if str(self.data["job_type"]) == "walk-in":
                if (
                    "walkin_to_date" in self.cleaned_data.keys()
                    and self.cleaned_data["walkin_to_date"] > date_time.date()
                ):
                    return date_time
                else:
                    raise serializers.ValidationError(
                        "Published date must be less than walkin end date"
                    )
            return date_time

    def validate_min_salary(self):
        if self.cleaned_data.get("min_salary"):
            try:
                min_sal = int(self.cleaned_data["min_salary"])
                return min_sal
            except:
                raise serializers.ValidationError("Minimum salary must be an Integer")
        else:
            return 0

    def validate_max_salary(self):
        if self.cleaned_data.get("min_salary") and self.cleaned_data.get("max_salary"):
            if int(self.cleaned_data["max_salary"]) < int(
                self.cleaned_data["min_salary"]
            ):
                raise serializers.ValidationError(
                    "Maximum salary must be greater than minimum salary"
                )
            return self.cleaned_data["max_salary"]
        elif self.cleaned_data.get("max_salary"):
            return self.cleaned_data["max_salary"]
        return 0

    def validate_company_name(self):
        return self.data["company_name"]

    def validate_company_website(self):
        if "company_website" in self.data and self.data["company_website"]:
            if (
                re.match(r"^http://", self.data["company_website"])
                or re.match(r"^https://", self.data["company_website"])
                or re.match(r"^www.", self.data["company_website"])
            ):

                company = ""
                if "company_id" in self.data.keys() and self.data["company_id"]:
                    company = Company.objects.filter(id=self.data["company_id"])
                if company:
                    companies = Company.objects.filter(
                        website__iexact=self.data["company_website"]
                    ).exclude(id=self.data["company_id"])
                    if companies:
                        raise serializers.ValidationError(
                            "Company with this website already exists"
                        )
                return self.cleaned_data["company_website"]
            else:
                raise serializers.ValidationError(
                    "Please include website with http:// or https:// or www."
                )

    def validate_company_logo(self):
        company_logo = self.cleaned_data.get("company_logo")
        if company_logo:
            sup_formates = ["image/jpeg", "image/png"]
            ftype = company_logo.content_type
            if str(ftype) not in sup_formates:
                raise serializers.ValidationError(
                    "Please upload Valid Image Format Ex: PNG, JPEG, JPG"
                )
            return company_logo
        return company_logo

    def validate_pincode(self):
        pincode = self.cleaned_data.get("pincode")
        if pincode:
            match = re.findall(r"\d{6}", pincode)
            if not match or len(pincode) != 6:
                raise serializers.ValidationError("Please Enter 6 digit valid Pincode")
        return pincode


class UserUpdateSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(required=False, input_formats=("%m/%d/%Y",))
    first_name = serializers.CharField(max_length=30)
    city = serializers.CharField(max_length=50)
    state = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=30)
    mobile = serializers.CharField(required=True)
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "nationality",
            "mobile",
            "technical_skills",
            "industry",
            "functional_area",
            "year",
            "month",
            "profile_description",
            "job_role",
            "state",
            "city",
            "dob",
            "job_role",
        ]

    def __init__(self, *args, **kwargs):
        super(UserUpdateSerializer, self).__init__(*args, **kwargs)
        if "dob" in self.initial_data.keys() and self.initial_data["dob"]:
            self.fields["dob"].required = True

    def clean_mobile(self):
        users = User.objects.filter(mobile=self.initial_data["mobile"]).exclude(
            id=int(self.initial_data["user_id"])
        )
        mobile = str(self.initial_data["mobile"])
        if not users:
            length = len(mobile) < 10 or len(mobile) > 12
            symbols = bool(
                re.search(r"[~\.,!@#\$%\^&\*\(\)_\{}\":;'\[\]]", mobile)
            ) or bool(re.search("[a-zA-Z]", mobile))
            if length or symbols:
                raise serializers.ValidationError("Please Enter Valid phone number")
            else:
                return mobile
        else:
            raise serializers.ValidationError(
                "User with this mobile number already exists"
            )


class ChangePasswordSerializer(serializers.Serializer):
    oldpassword = serializers.CharField(
        max_length=50,
        error_messages={
            "required": "Please enter your current password",
            "invalid": "Enter a valid email",
        },
    )
    newpassword = serializers.CharField(
        max_length=50,
        error_messages={
            "required": "Please enter new password",
            "invalid": "Enter a valid email",
        },
    )
    retypepassword = serializers.CharField(
        max_length=50,
        error_messages={
            "required": "Please enter confirm password",
            "invalid": "Enter a valid email",
        },
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(ChangePasswordSerializer, self).__init__(*args, **kwargs)

    def validate_oldpassword(self, oldpassword):
        if not check_password(oldpassword, self.user.password):
            raise serializers.ValidationError("The current password is not correct")
        return oldpassword

    def validate(self, data):
        if data["newpassword"] != data["retypepassword"]:
            raise serializers.ValidationError(
                "New password and Confirm password should match"
            )
        else:
            return data["newpassword"]


class MenuSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"
