import hashlib
import json
import uuid
import os
from datetime import datetime
import re
import arrow
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

# from oauth2client.contrib.django_util.models import CredentialsField

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q, Count, F, JSONField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# from microurl import google_mini

COMPANY_SIZE = (
    ("1-10", "1-10"),
    ("11-20", "11-20"),
    ("21-50", "21-50"),
    ("50-200", "50-200"),
    ("200+", "200+"),
)

STATUS = (
    ("Active", "Active"),
    ("InActive", "InActive"),
)

current_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").strftime(
    "%Y-%m-%d"
)


class Industry(models.Model):
    name = models.CharField(max_length=500)
    status = models.CharField(choices=STATUS, max_length=10)
    slug = models.SlugField(max_length=500)
    meta_title = models.TextField(default="")
    meta_description = models.TextField(default="")
    page_content = models.TextField(default="")

    def get_job_url(self):
        job_url = "/" + str(self.slug) + "-industry-jobs/"
        return job_url

    def get_no_of_jobposts(self):
        return JobPost.objects.filter(industry__in=[self], status="Live")

    def get_no_of_all_jobposts(self):
        return JobPost.objects.filter(industry__in=[self])


class Keyword(models.Model):
    name = models.CharField(max_length=1000)


USER_TYPE = (
    ("JS", "Job Seeker"),
    ("RR", "Recruiter"),
    ("RA", "Recruiter Admin"),
    ("AA", "Agency Admin"),
    ("AR", "Agency Recruiter"),
)

GENDER_TYPES = (
    ("F", "Female"),
    ("M", "Male"),
)

STATUS_TYPES = (
    ("Enabled", "Enabled"),
    ("Disabled", "Disabled"),
)

DEGREE_TYPES = (
    ("Permanent", "Permanent"),
    ("PartTime", "PartTime"),
)

COMPANY_TYPES = (
    ("Consultant", "consultant"),
    ("Company", "company"),
)


def img_url(self, filename):
    hash_ = hashlib.md5()
    hash_.update(str(filename).encode("utf-8") + str(datetime.now()).encode("utf-8"))
    file_hash = hash_.hexdigest()

    if self.__class__.__name__ == "Company":
        # parsed_target_url = urlparse(self.website)
        # domain = str(parsed_target_url.netloc).split('.')[0]
        filename = self.slug + "." + str(filename.split(".")[-1])
    else:
        filename = filename
    return "%s%s/%s" % (self.file_prepend, file_hash, filename)


class Qualification(models.Model):
    name = models.CharField(max_length=500)
    status = models.CharField(choices=STATUS, max_length=10)
    slug = models.SlugField(max_length=500)

    def __str__(self):
        return self.name

    def get_no_of_jobposts(self):
        return JobPost.objects.filter(edu_qualification__in=[self])


class Country(models.Model):
    name = models.CharField(max_length=500)
    status = models.CharField(choices=STATUS_TYPES, max_length=10, default="Enabled")
    slug = models.SlugField(max_length=500, default="")

    def __str__(self):
        return self.name

    def get_no_of_jobposts(self):
        return JobPost.objects.filter(location__state__country=self, status="Live")


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    name = models.CharField(max_length=500)
    status = models.CharField(choices=STATUS_TYPES, max_length=10, default="Enabled")
    slug = models.SlugField(max_length=500, default="")

    def __str__(self):
        return self.name

    def get_no_of_jobposts(self):
        return JobPost.objects.filter(
            location__in=City.objects.filter(state=self), status="Live"
        )

    def get_state_cities(self):
        cities = (
            self.state.annotate(num_posts=Count("locations"))
            .filter(status="Enabled")
            .exclude(name=F("state__name"))
            .order_by("-num_posts")
        )
        return cities[:5]


SKILL_TYPE = (("it", "IT"), ("non-it", "Non-IT"), ("other", "Other"))


class Skill(models.Model):
    name = models.CharField(max_length=500)
    status = models.CharField(choices=STATUS, max_length=10)
    icon = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=500)
    meta_title = models.TextField(default="")
    meta_description = models.TextField(default="")
    page_content = models.TextField(default="")
    meta = models.JSONField(null=True)
    skill_type = models.CharField(choices=SKILL_TYPE, max_length=20, default="it")

    def __str__(self):
        return self.name

    def get_job_url(self):
        job_url = "/" + str(self.slug) + "-jobs/"
        return job_url

    def get_no_of_jobposts(self):
        return JobPost.objects.filter(skills__in=[self], status="Live")

    def get_no_of_jobposts_all(self):
        return JobPost.objects.filter(skills__in=[self])

    def get_no_of_subscriptions(self):
        return Subscriber.objects.filter(skill=self)

    def get_no_of_applicants(self):
        return User.objects.filter(skills__skill=self)

    def get_no_of_resume_applicants(self):
        return AgencyResume.objects.filter(skill=self)

    def get_meta_data(self):
        if self.meta:
            return json.dumps(self.meta)
        else:
            return ""


class FunctionalArea(models.Model):
    name = models.CharField(max_length=500, unique=True)
    status = models.CharField(choices=STATUS, max_length=10)
    slug = models.SlugField(max_length=500)

    def __str__(self):
        return self.name

    def get_no_of_jobposts(self):
        return JobPost.objects.filter(functional_area__in=[self])


class Language(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class UserLanguage(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    write = models.BooleanField(default=False)
    speak = models.BooleanField(default=False)


class City(models.Model):
    name = models.CharField(max_length=500)
    state = models.ForeignKey(State, related_name="state", on_delete=models.PROTECT)
    status = models.CharField(choices=STATUS_TYPES, max_length=10, default="Enabled")
    slug = models.SlugField(max_length=500)
    internship_text = models.CharField(max_length=1000)
    meta_title = models.TextField(default="")
    meta_description = models.TextField(default="")
    internship_meta_title = models.TextField(default="")
    internship_meta_description = models.TextField(default="")
    page_content = models.TextField(default="")
    internship_content = models.TextField(default="")
    meta = JSONField(null=True)

    def __str__(self):
        return self.name

    def get_job_url(self):
        job_url = "/jobs-in-" + str(self.slug) + "/"
        return job_url

    def get_no_of_jobposts(self):
        return JobPost.objects.filter(location__in=[self], status="Live")

    def get_no_of_all_jobposts(self):
        return JobPost.objects.filter(location__in=[self])

    def get_meta_data(self):
        if self.meta:
            return json.dumps(self.meta)
        else:
            return ""


class Company(models.Model):
    file_prepend = "company/logo/"
    name = models.CharField(max_length=5000)
    website = models.CharField(max_length=5000, null=True, blank=True)
    address = models.TextField()
    profile_pic = models.FileField(
        max_length=1000, upload_to=img_url, null=True, blank=True
    )
    size = models.CharField(choices=COMPANY_SIZE, max_length=10, default="")
    level = models.IntegerField(null=True, blank=True)
    company_type = models.CharField(choices=COMPANY_TYPES, max_length=50, default="")
    profile = models.TextField()
    phone_number = models.CharField(max_length=15)
    registered_date = models.DateField(auto_now_add=True)
    email = models.EmailField(max_length=255, null=True)
    short_code = models.CharField(max_length=50, null=True)
    is_active = models.BooleanField(default=False)
    slug = models.SlugField(max_length=5000)
    meta_title = models.TextField(default="")
    meta_description = models.TextField(default="")
    campaign_icon = models.CharField(max_length=3000, null=True)
    created_from = models.CharField(max_length=200, default="")

    def is_company(self):
        if str(self.company_type) == "Company":
            return True
        return False

    def is_agency(self):
        if str(self.company_type) == "Consultant":
            return True
        return False

    def get_company_admin(self):
        return User.objects.filter(is_admin=True, company=self).first()

    def get_company_recruiters(self):
        return User.objects.filter(company=self)

    def get_company_jobposts(self):
        return JobPost.objects.filter(user__company=self)

    def get_jobposts(self):
        return JobPost.objects.filter(company=self, status="Live")

    def get_total_jobposts(self):
        return JobPost.objects.filter(company=self)

    def get_company_tickets(self):
        return Ticket.objects.filter(user__company=self)

    def get_company_menu(self):
        return Menu.objects.filter(company=self)

    def get_active_company_menu(self):
        return Menu.objects.filter(company=self, status=True).order_by("id")

    def get_live_jobposts(self):
        return JobPost.objects.filter(user__company=self, status="Live")

    def get_unique_recruiters(self):
        job_posts = list(
            set(
                list(
                    JobPost.objects.filter(company=self, status="Live").values_list(
                        "user", flat=True
                    )
                )
            )
        )
        users = User.objects.filter(id__in=job_posts)
        return users

    def get_absolute_url(self):
        return "/" + str(self.slug) + "-job-openings/"

    def get_logo_url(self):
        if self.profile_pic:
            return str(self.profile_pic)
        return "https://cdn.peeljobs.com/static/company_logo.png"

    def get_description(self):
        from bs4 import BeautifulSoup

        html = self.profile
        # create a new bs4 object from the html data loaded
        soup = BeautifulSoup(html)
        # remove all javascript and stylesheet code
        for script in soup(["script", "style"]):
            script.extract()
        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = "\n<br>".join(chunk for chunk in chunks if chunk)
        return text

    def get_website(self):
        site = self.website
        if site is not None and "//" in site:
            site = site.split("//")[1]
        return site

    def get_logo_url(self):
        if self.profile_pic:
            return str(self.profile_pic)
        return "https://cdn.peeljobs.com/static/company_logo.png"


class EducationInstitue(models.Model):
    name = models.CharField(max_length=500)
    address = models.CharField(max_length=2000, default="")
    city = models.ForeignKey(City, on_delete=models.PROTECT)


class EmploymentHistory(models.Model):
    company = models.CharField(max_length=500)
    from_date = models.DateField(null=True)
    to_date = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=500)
    current_job = models.BooleanField(default=False)
    job_profile = models.TextField()


class Degree(models.Model):
    degree_name = models.ForeignKey(Qualification, on_delete=models.PROTECT)
    degree_type = models.CharField(choices=DEGREE_TYPES, max_length=50)
    specialization = models.CharField(max_length=500)


class EducationDetails(models.Model):
    institute = models.ForeignKey(EducationInstitue, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField(null=True, blank=True)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    score = models.CharField(max_length=50)
    current_education = models.BooleanField(default=False)


class Project(models.Model):
    name = models.CharField(max_length=500)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    skills = models.ManyToManyField(Skill)
    description = models.TextField(max_length=2000, default="")
    location = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=500, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)


TechnicalSkill_STATUS = (
    ("Poor", "Poor"),
    ("Average", "Average"),
    ("Good", "Good"),
    ("Expert", "Expert"),
)


class TechnicalSkill(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    last_used = models.DateField(null=True, blank=True)
    version = models.CharField(max_length=100, null=True, blank=True)
    proficiency = models.CharField(
        choices=TechnicalSkill_STATUS, max_length=100, null=True, blank=True
    )
    is_major = models.BooleanField(default=False)


class Certification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_certifications')
    name = models.CharField(max_length=500)
    organization = models.CharField(max_length=500)
    credential_id = models.CharField(max_length=200, null=True, blank=True)
    credential_url = models.URLField(max_length=1000, null=True, blank=True)
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    does_not_expire = models.BooleanField(default=False)
    description = models.TextField(max_length=2000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.organization}"

    class Meta:
        ordering = ['-issued_date', '-created_at']


MARTIAL_STATUS = (
    ("Single", "Single"),
    ("Married", "Married"),
)

REGISTERED_FROM = (
    ("Email", "Email"),
    ("Social", "Social"),
    ("ResumePool", "ResumePool"),
    ("Resume", "Resume"),
    ("Careers", "Careers"),
)


def resume_upload_path(instance, filename):
    """
    Generate a secure upload path for resume files using UUID for better randomness.
    Path format: resume/user_{user_id}/{year}/{month}/{uuid}_{original_filename}
    """
    # Get file extension
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Generate UUID for uniqueness
    unique_id = uuid.uuid4().hex
    
    # Get current date for organization
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    
    # Clean the original filename (remove spaces, special chars)
    clean_filename = re.sub(r'[^\w\-_\.]', '_', filename)
    clean_filename = re.sub(r'_+', '_', clean_filename)  # Replace multiple underscores with single
    
    # Create new filename with UUID prefix
    new_filename = f"{unique_id}_{clean_filename}"
    
    # Return the full path
    return f"resume/user_{instance.id}/{year}/{month}/{new_filename}"


class User(AbstractBaseUser, PermissionsMixin):
    file_prepend = "user/img/"
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    company = models.ForeignKey(
        Company, blank=True, null=True, on_delete=models.SET_NULL
    )
    profile_pic = models.FileField(
        max_length=1000, upload_to=img_url, null=True, blank=True
    )
    user_type = models.CharField(choices=USER_TYPE, max_length=10)
    signature = models.CharField(max_length=2000, default="")
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(_("staff status"), default=False)
    gender = models.CharField(
        choices=GENDER_TYPES, max_length=10, blank=True, null=True
    )
    address = models.TextField(max_length=1000, blank=True, null=True)
    permanent_address = models.TextField(max_length=1000, blank=True, null=True)
    nationality = models.TextField(max_length=50, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    alternate_mobile = models.BigIntegerField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    email_verified = models.BooleanField(default=False)
    city = models.ForeignKey(
        City, null=True, blank=True, related_name="user_city", on_delete=models.SET_NULL)

    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(
        Country, null=True, blank=True, on_delete=models.SET_NULL)

    pincode = models.IntegerField(null=True, blank=True)
    last_password_reset_on = models.DateTimeField(auto_now_add=True)
    photo = models.CharField(max_length=500)
    marital_status = models.CharField(
        choices=MARTIAL_STATUS, max_length=50, blank=True, null=True
    )
    employment_history = models.ManyToManyField(EmploymentHistory)
    current_city = models.ForeignKey(
        'City', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    preferred_city = models.ManyToManyField(City, related_name="preferred_city")
    functional_area = models.ManyToManyField(FunctionalArea)
    job_role = models.CharField(max_length=500, default="")
    education = models.ManyToManyField(EducationDetails)
    project = models.ManyToManyField(Project)
    skills = models.ManyToManyField(TechnicalSkill)
    language = models.ManyToManyField(UserLanguage)
    current_salary = models.CharField(max_length=50, blank=True, null=True)
    expected_salary = models.CharField(max_length=500, blank=True, null=True)
    prefered_industry = models.ForeignKey(
        Industry, blank=True, null=True, on_delete=models.SET_NULL)
    
    industry = models.ManyToManyField(Industry, related_name="recruiter_industries")
    technical_skills = models.ManyToManyField(Skill, related_name="recruiter_skill")
    dob = models.DateField(blank=True, null=True)
    profile_description = models.CharField(max_length=5000, default="")
    # Resume file with UUID-based upload path for secure storage
    resume = models.FileField(
        upload_to=resume_upload_path,
        max_length=2000,
        null=True,
        blank=True,
        help_text='Upload your resume in PDF, DOC, DOCX, RTF, or ODT format (max 1MB)'
    )
    relocation = models.BooleanField(default=False)
    notice_period = models.CharField(max_length=50, blank=True, null=True)
    year = models.CharField(max_length=50, blank=True, null=True)
    month = models.CharField(max_length=50, default="")
    show_email = models.BooleanField(default=False)
    resume_title = models.TextField(max_length=2000, blank=True, null=True)
    resume_text = models.TextField(blank=True, null=True)
    mobile_verification_code = models.CharField(max_length=50, default="")
    last_mobile_code_verified_on = models.DateTimeField(auto_now_add=True)
    mobile_verified = models.BooleanField(default=False)
    is_login = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    profile_updated = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)  # agency created user
    profile_completeness = models.CharField(max_length=500, default="")
    activation_code = models.CharField(max_length=100, null=True, blank=True)
    # is_register_through_mail = models.BooleanField(default=False)
    registered_from = models.CharField(
        choices=REGISTERED_FROM, max_length=15, default=""
    )
    is_unsubscribe = models.BooleanField(default=False)
    is_bounce = models.BooleanField(default=False)
    unsubscribe_code = models.CharField(max_length=100, null=True, blank=True)
    # Other admins in agency other than agency created user
    agency_admin = models.BooleanField(default=False)
    referer = models.TextField(null=True, blank=True)
    unsubscribe_reason = models.TextField(default="")
    is_looking_for_job = models.BooleanField(default=False)
    is_open_to_offers = models.BooleanField(default=False)

    # Password reset fields
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_staff:
            return True
        # return _user_has_perm(self, perm, obj)
        else:
            try:
                user_perm = self.user_permissions.get(codename=perm)
            except ObjectDoesNotExist:
                user_perm = False
            if user_perm:
                return True
            else:
                return False

    class Meta:
        permissions = (
            ("support_view", "can view tickets"),
            ("support_edit", "can edit tickets"),
            ("activity_view", "can view recruiters, applicants, data, posts"),
            ("activity_edit", "can edit data"),
            ("jobposts_edit", "can manage jobposts"),
            ("jobposts_invoice_access", "can manage invoice"),
            ("jobposts_resume_profiles", "can manage resume profiles"),
        )

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = "%s %s" % (
            self.first_name,
            self.last_name if self.last_name else "",
        )
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def get_full_username(self):
        return " ".join(re.findall("[a-zA-Z]+", self.username))

    def get_user_type_display(self):
        """Return human-readable user type for display purposes"""
        user_type_dict = dict(USER_TYPE)
        return user_type_dict.get(self.user_type, self.user_type)

    @property
    def is_fb_connected(self):
        if self.facebook_user.all():
            return True
        else:
            return False

    @property
    def is_gp_connected(self):
        if self.google_user.all():
            return True
        else:
            return False

    @property
    def is_gh_connected(self):
        if self.github.all():
            return True
        else:
            return False

    @property
    def is_recruiter(self):
        if (
            str(self.user_type) == "RR"
            or str(self.user_type) == "RA"
            or str(self.user_type) == "RA"
        ):
            return True
        else:
            return False


    @property
    def is_connect_social_networks(self):
        if (
            self.facebook_user.all()
            and self.google_user.all()
        ):
            return True
        else:
            return False

    @property
    def is_recruiter_active(self):
        if self.is_connect_social_networks and self.is_active and self.mobile_verified:
            return True
        else:
            return False

    def is_company_recruiter(self):
        if self.is_recruiter:
            return True
        else:
            return False

    @property
    def is_agency_recruiter(self):
        if self.company and str(self.company.company_type) == "Consultant":
            return True
        return False

    @property
    def is_agency_admin(self):
        if self.company and self.agency_admin:
            return True
        return False

    @property
    def is_jobseeker(self):
        if str(self.user_type) == "JS":
            return True
        return False

    @property
    def profile_completion_percentage(self):
        complete = 0
        if self.year:
            complete += 10
        if self.mobile:
            complete += 20
        if self.is_active:
            complete += 10
        if self.user_type == "JS":
            if self.resume:
                complete += 15
            if len(self.profile_description):
                complete += 5
            if self.education.all():
                complete += 10
            if self.project.all():
                complete += 10
            if self.skills.all():
                complete += 15
            if self.language.all():
                complete += 5
        else:
            if self.job_role:
                complete += 10
            if self.industry.all():
                complete += 10
            if self.profile_description:
                complete += 15
            if self.technical_skills.all():
                complete += 15
            if self.functional_area.all():
                complete += 10
        return complete

    def get_jobposts_count(self):
        return len(JobPost.objects.filter(user=self))

    def get_total_job_post_views_count(self):
        job_posts = JobPost.objects.filter(user=self)
        total_views = 0
        for each in job_posts:
            total_views = (
                each.fb_views + each.tw_views + each.ln_views + each.other_views
            )
        return total_views

    def get_total_jobposts(self):
        return JobPost.objects.filter(user=self)

    def get_active_jobposts_count(self):
        return len(JobPost.objects.filter(user=self, status="Live"))

    def get_inactive_jobposts_count(self):
        return len(
            JobPost.objects.filter(
                Q(user=self) & Q(status="Disabled") | Q(status="Expired")
            )
        )

    def get_applied_users(self):
        return AppliedJobs.objects.filter(job_post__user=self, status="Pending")

    def get_applied_jobs(self):
        ids = (
            AppliedJobs.objects.filter(user=self)
            .exclude(ip_address="", user_agent="")
            .values_list("job_post", flat=True)
        )
        applied_jobs = JobPost.objects.filter(id__in=ids)
        return applied_jobs

    def get_all_applied_jobs(self):
        return AppliedJobs.objects.filter(user=self).select_related("job_post")

    def get_facebook_id(self):
        return Facebook.objects.filter(user=self).first().facebook_id

    def get_facebook_url(self):
        return Facebook.objects.filter(user=self).first().facebook_url

    def get_google_url(self):
        return Google.objects.filter(user=self).first().google_url

    def get_user_emails(self):
        return UserEmail.objects.filter(user=self)

    def get_open_tickets(self):
        return Ticket.objects.filter(
            Q(user=self) & Q(status="Open") | Q(status="Ongoing")
        )

    def get_closed_tickets(self):
        return Ticket.objects.filter(user=self, status="Closed")

    def get_major_skills(self):
        return self.skills.filter(is_major=True)

    def get_search_done(self):
        return SearchResult.objects.filter(user=self)

    def get_visited_jobs(self):
        return VisitedJobs.objects.filter(user=self)

    def get_facebook_object(self):
        return self.facebook_user.all().first()

    def get_google_object(self):
        return self.google_user.all().first()

    def get_github_object(self):
        return self.google_user.all().first()

    def get_subscribed_skills(self):
        user_emails = (
            UserEmail.objects.filter(user=self)
            .values_list("email", flat=True)
            .distinct()
        )
        return Skill.objects.filter(
            id__in=Subscriber.objects.filter(
                email__in=user_emails, is_verified=True
            ).values_list("skill", flat=True)
        ).distinct()

    def get_jobs_list(self):
        job_posts = JobPost.objects.filter(user=self)
        return job_posts

    def get_live_jobs_list(self):
        job_posts = JobPost.objects.filter(user=self, status="Live")
        return job_posts

    def get_tickets_list(self):
        tickets = Ticket.objects.filter(user=self)
        return tickets

    def get_assigned_jobs_list(self):
        job_posts = JobPost.objects.filter(agency_recruiters__in=[self]).exclude(
            status="Hired"
        )
        return job_posts

    def get_resumes_uploaded(self):
        agency_resumes = AgencyResume.objects.filter(uploaded_by=self)
        return agency_resumes

    def get_selected_applicants(self):
        selected_applicants = AgencyApplicants.objects.filter(
            applicant__uploaded_by=self, created_on__date=current_date
        )
        return selected_applicants

    def get_hired_applicants(self):
        selected_applicants = AgencyApplicants.objects.filter(
            applicant__uploaded_by=self, created_on__date=current_date
        )
        return selected_applicants

    # def is_agency_admin(self, job_post_id):
    #     job_post = get_object_or_404(JobPost, id=job_post_id)

    #     if self.company == job_post.user.company and str(self.user_type) == 'AA' and self.is_admin:
    #         return True
    #     return False
    def get_user_login_only_once(self):
        last_login = arrow.get(self.last_login).format("YYYY-MM-DD HH:mm:ss")
        date_joined = arrow.get(self.date_joined).format("YYYY-MM-DD HH:mm:ss")
        if str(last_login) == str(date_joined):
            return True
        else:
            self.is_login = True
            self.save()
            return False

    def get_email_name(self):
        user = User.objects.filter(id=self.id)[0]
        if "@" in user.username:
            return user.username.split("@")[0]
        return user.username

    def get_user_alerts(self):
        return JobAlert.objects.filter(email=self.email)

    def related_walkin_jobs(self):
        skill_ids = self.skills.all().values_list("skill_id", flat=True)
        job_posts = JobPost.objects.filter(status="Live", job_type="walk-in")
        job_posts = job_posts.filter(skills__in=Skill.objects.filter(id__in=skill_ids))
        if len(job_posts) > 0:
            if len(job_posts) < 15:
                all_job_posts = JobPost.objects.filter(status="Live").order_by(
                    "-published_on"
                )
                rest = 15 - len(job_posts)
                job_posts = list(job_posts) + list(all_job_posts[:rest])
        else:
            job_posts = JobPost.objects.filter(
                status="Live", job_type="walk-in"
            ).order_by("-published_on")[:15]
        return job_posts

    def related_jobs(self):
        ids = (
            AppliedJobs.objects.filter(user=self)
            .exclude(ip_address="", user_agent="")
            .values_list("job_post", flat=True)
        )
        user_skills = Skill.objects.filter(id__in=self.skills.all().values("skill"))
        related_jobs = JobPost.objects.filter(
            Q(status="Live") & Q(skills__in=user_skills)
            | Q(location__in=[self.current_city])
        ).exclude(id__in=ids)
        related_jobs = list(related_jobs) + list(
            JobPost.objects.filter(status="Live").order_by("-published_on")[:15]
        )
        return related_jobs[:15]

    def get_similar_recruiters(self):
        if self.agency_admin:
            return User.objects.filter(company=self.company)
        jobs = AgencyRecruiterJobposts.objects.filter(user=self).values("job_post")
        users = AgencyRecruiterJobposts.objects.filter(job_post__in=jobs).values("user")
        return User.objects.filter(id__in=users)


PRIORITY_TYPES = (
    ("Low", "Low"),
    ("Normal", "Normal"),
    ("High", "High"),
)

TICKET_TYPES = (
    ("Bug", "Bug"),
    ("Feature", "Feature"),
    ("Enhancement", "Enhancement"),
    ("Performance", "Performance"),
    ("Design", "Design"),
    ("Other", "Other"),
)

STATUS = (
    ("Open", "Open"),
    ("Closed", "Closed"),
    ("Ongoing", "Ongoing"),
)


class Attachment(models.Model):
    file_prepend = "ticket/attachments/"
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    attached_file = models.FileField(
        max_length=500, null=True, blank=True, upload_to=img_url
    )


class Ticket(models.Model):
    user = models.ForeignKey(User, related_name="ticket", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    attachments = models.ManyToManyField(Attachment, blank=True)
    priority = models.CharField(choices=PRIORITY_TYPES, max_length=20)
    ticket_type = models.CharField(choices=TICKET_TYPES, max_length=20)
    status = models.CharField(choices=STATUS, max_length=20)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=1, blank=True)

    def get_ticket_comments(self):
        return Comment.objects.filter(ticket=self)

    def get_ticket_attachments(self):
        return self.attachments.filter()


class Comment(models.Model):
    comment = models.TextField(blank=True)
    commented_by = models.ForeignKey(
        User, related_name="comments", on_delete=models.CASCADE
    )
    ticket = models.ForeignKey(Ticket, related_name="ticket", on_delete=models.CASCADE)
    attachments = models.ManyToManyField(Attachment, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def get_comments_attatchments(self):
        return self.attachments.filter()


class UserEmail(models.Model):
    user = models.ForeignKey(User, related_name="user_email", on_delete=models.CASCADE)
    email = models.EmailField(max_length=100)
    is_primary = models.BooleanField(default=False)


class Facebook(models.Model):
    user = models.ForeignKey(
        User, related_name="facebook_user", on_delete=models.CASCADE
    )
    facebook_id = models.CharField(max_length=100)
    facebook_url = models.CharField(max_length=200, default="")
    first_name = models.CharField(max_length=200, default="")
    last_name = models.CharField(max_length=200, default="")
    verified = models.CharField(max_length=200, default="")
    name = models.CharField(max_length=200, default="")
    language = models.CharField(max_length=200, default="")
    hometown = models.CharField(max_length=200, default="")
    email = models.CharField(max_length=200, default="", db_index=True)
    gender = models.CharField(max_length=200, default="")
    dob = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, default="")
    timezone = models.CharField(max_length=200, default="")
    accesstoken = models.CharField(max_length=2000, default="")


class Google(models.Model):
    user = models.ForeignKey(User, related_name="google_user", on_delete=models.CASCADE)
    google_id = models.CharField(max_length=200, default="")
    google_url = models.CharField(max_length=1000, default="")
    verified_email = models.CharField(max_length=200, default="")
    family_name = models.CharField(max_length=200, default="")
    name = models.CharField(max_length=200, default="")
    picture = models.CharField(max_length=200, default="")
    gender = models.CharField(max_length=10, default="")
    dob = models.CharField(max_length=50, default="")
    given_name = models.CharField(max_length=200, default="")
    email = models.CharField(max_length=200, default="", db_index=True)


class GitHub(models.Model):
    user = models.ForeignKey(User, related_name="github", on_delete=models.CASCADE)
    git_url = models.URLField()
    git_id = models.CharField(max_length=50)
    disk_usage = models.CharField(max_length=200)
    private_gists = models.IntegerField(default=0)
    public_gists = models.IntegerField(default=0)
    public_repos = models.IntegerField(default=0)
    hireable = models.BooleanField(default=False)
    total_private_repos = models.IntegerField(default=0)
    owned_private_repos = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    company = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    user_from = models.DateTimeField()


class InterviewLocation(models.Model):
    venue_details = models.TextField()
    show_location = models.BooleanField(default=False)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)

    def get_map_coordinates_list(self):
        coordinates = []
        coordinates.append(str(self.id))
        coordinates.append(self.latitude)
        coordinates.append(self.longitude)
        return json.dumps(coordinates)

    def get_coordinates_list(self):
        coordinates = []
        coordinates.append(self.latitude)
        coordinates.append(self.longitude)
        return json.dumps(coordinates)


GOV_JOB_TYPE = (
    ("Central", "Central"),
    ("State", "State"),
)

JOB_TYPE = (
    ("full-time", "Full Time"),
    ("internship", "Internship"),
    ("walk-in", "Walk-in"),
    ("government", "Government"),
    ("Fresher", "Fresher"),
)

WALKIN_TYPE = (
    ("this_week", "This Week"),
    ("this_month", "This Month"),
    ("next_week", "Next Week"),
    ("custom_range", "Custom Range"),
)

AGENCY_JOB_TYPE = (
    ("Permanent", "Permanent"),
    ("Contract", "Contract"),
)

AGENCY_INVOICE_TYPE = (
    ("Recurring", "Recurring"),
    ("Non_Recurring", "Non Recurring"),
)

MONTHS = (
    ("January", "January"),
    ("February", "February"),
    ("March", "March"),
    ("April", "April"),
    ("May", "May"),
    ("June", "June"),
    ("July", "July"),
    ("August", "August"),
    ("September", "September"),
    ("October", "October"),
    ("November", "November"),
    ("December", "December"),
)


class AgencyCompanyBranch(models.Model):
    location = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField()
    contact_details = models.TextField()
    is_major = models.BooleanField(default=False)


class AgencyCompanyCatogery(models.Model):
    name = models.CharField(max_length=1000)
    percantage = models.CharField(max_length=255, default="")


class AgencyContractDetails(models.Model):
    month = models.CharField(choices=MONTHS, max_length=50)
    percantage = models.CharField(max_length=255, default="")


class AgencyCompany(models.Model):
    file_prepend = "agencycompany/logo/"
    name = models.CharField(max_length=255)
    website = models.URLField()
    decription = models.TextField()
    logo = models.FileField(upload_to=img_url, null=True, blank=True)
    branch_details = models.ManyToManyField(AgencyCompanyBranch)
    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.RESTRICT
    )
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, null=True, blank=True)
    company_categories = models.ManyToManyField(
        AgencyCompanyCatogery, related_name="categories"
    )
    contract_details = models.ManyToManyField(
        AgencyContractDetails, related_name="contract_details"
    )


class JobPostManager(models.Manager):
    def get_queryset(self):
        return super(JobPostManager, self).get_queryset().order_by("-created_on")


class JobPost(models.Model):
    POST_STATUS = (
        ("Draft", "Draft"),
        ("Exprired", "Expired"),
        ("Live", "Live"),
        ("Disabled", "Disabled"),
        ("Pending", "Pending"),
        ("Published", "Published"),
        ("Hired", "Hired"),
        ("Process", "Process"),
    )
    SALARY_TYPE = (
        ("Month", "Month"),
        ("Year", "Year"),
    )
    user = models.ForeignKey(User, related_name="jobposts", on_delete=models.CASCADE)
    code = models.CharField(max_length=50, null=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=5000)
    location = models.ManyToManyField(City, related_name="locations")
    job_role = models.CharField(max_length=50, default="")
    vacancies = models.IntegerField()
    industry = models.ManyToManyField(Industry)
    job_interview_location = models.ManyToManyField(InterviewLocation)
    country = models.ForeignKey(
        Country, null=True, related_name="job_country", on_delete=models.SET_NULL)
    
    functional_area = models.ManyToManyField(FunctionalArea)
    keywords = models.ManyToManyField(Keyword)
    description = models.TextField()
    min_year = models.IntegerField(default=0)
    min_month = models.IntegerField(default=0)
    max_year = models.IntegerField(default=0)
    max_month = models.IntegerField(default=0)
    fresher = models.BooleanField(default=False)
    edu_qualification = models.ManyToManyField(Qualification)
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    pincode = models.CharField(max_length=50, blank=True, null=True)
    # tech_qualification =

    # govt jobpost
    application_fee = models.IntegerField(default=0)
    govt_job_type = models.CharField(
        choices=GOV_JOB_TYPE, max_length=50, default="Central"
    )
    selection_process = models.TextField(default="")
    how_to_apply = models.TextField(default="")
    important_dates = models.TextField(default="")
    # validity
    govt_from_date = models.DateField(null=True, blank=True)
    govt_to_date = models.DateField(null=True, blank=True)
    govt_exam_date = models.DateField(null=True, blank=True)
    age_relaxation = models.TextField(default="")

    walkin_contactinfo = models.TextField(default="")
    walkin_show_contact_info = models.BooleanField(default=False)
    walkin_from_date = models.DateField(null=True, blank=True)
    walkin_to_date = models.DateField(null=True, blank=True)
    walkin_time = models.TimeField(blank=True, null=True)

    agency_job_type = models.CharField(
        choices=AGENCY_JOB_TYPE, max_length=50, default="Permanent"
    )
    agency_invoice_type = models.CharField(
        choices=AGENCY_INVOICE_TYPE, max_length=50, default="Recurring"
    )
    agency_amount = models.CharField(max_length=1000, default="")
    agency_recruiters = models.ManyToManyField(User, related_name="recruiters")
    agency_client = models.ForeignKey(
        AgencyCompany, null=True, on_delete=models.SET_NULL)

    send_email_notifications = models.BooleanField(default=False)
    agency_category = models.ForeignKey(
        AgencyCompanyCatogery, null=True, on_delete=models.SET_NULL)
    

    visa_required = models.BooleanField(default=False)
    visa_country = models.ForeignKey(
        Country, null=True, related_name="visa_country", on_delete=models.SET_NULL)
    
    visa_type = models.CharField(max_length=50, default="")
    skills = models.ManyToManyField(Skill)
    salary_type = models.CharField(
        choices=SALARY_TYPE, max_length=20, blank=True, null=True
    )
    min_salary = models.IntegerField(default=0)
    max_salary = models.IntegerField(default=0)
    last_date = models.DateField(null=True)
    published_on = models.DateTimeField(null=True, blank=True)
    published_date = models.DateTimeField(null=True, blank=True)
    posted_on = models.DateTimeField(auto_now=True)
    created_on = models.DateField(auto_now_add=True)
    status = models.CharField(choices=POST_STATUS, max_length=50)
    previous_status = models.CharField(
        choices=POST_STATUS, max_length=50, default="Draft"
    )
    post_on_fb = models.BooleanField(default=False)
    post_on_tw = models.BooleanField(default=False)
    post_on_ln = models.BooleanField(default=False)
    fb_views = models.IntegerField(default=0)
    tw_views = models.IntegerField(default=0)
    ln_views = models.IntegerField(default=0)
    other_views = models.IntegerField(default=0)
    job_type = models.CharField(choices=JOB_TYPE, max_length=50)
    published_message = models.TextField()
    company_name = models.CharField(max_length=100, default="")
    company_address = models.TextField()
    company_description = models.TextField()
    company_links = models.TextField()
    company_emails = models.EmailField(blank=True, null=True)
    meta_title = models.TextField()
    meta_description = models.TextField()
    major_skill = models.ForeignKey(
        Skill,
        null=True,
        blank=True,
        related_name="major_skill",
        on_delete=models.SET_NULL)
    
    closed_date = models.DateTimeField(null=True, blank=True)

    fb_groups = ArrayField(models.CharField(max_length=200), blank=True, null=True)

    # objects = JobPostManager()
    class Meta:
        ordering = ["-created_on"]

    def __unicode__(self):
        return self.title

    def get_data(self):
        return self

    def get_absolute_url(self):
        qs = self.title.replace("/[^a-zA-Z-]/g", "").title().strip().strip(".")
        qs = qs.replace(" ", "-").lower()
        qs = qs.replace("/", "-").replace(",", "").lower()
        qs = qs.replace(".", "dot-")
        if str(self.job_type) == "internship":
            if self.company:
                company_name = self.company.slug
            else:
                company_name = self.company_name
            qs = "/" + qs + "-" + str(company_name) + "-" + str(self.id) + "/"
        else:
            qs = (
                "/"
                + qs
                + "-"
                + str(self.min_year)
                + "-to-"
                + str(self.max_year)
                + "-years-"
                + str(self.id)
                + "/"
            )
        return qs

    def get_total_views_count(self):
        total_views = self.fb_views + self.tw_views + self.ln_views + self.other_views
        return total_views

    def get_similar_jobposts(self):
        # current_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").strftime("%Y-%m-%d")
        jobs = (
            JobPost.objects.filter(Q(skills__in=self.skills.all()))
            .filter(Q(min_year=self.min_year) | Q(max_year=self.max_year))
            .exclude(pk=self.id)
            .distinct()
        )
        jobs = (
            jobs.filter(status="Live")
            .select_related("company")
            .prefetch_related("location")
        )
        # no_of_jobs = len(jobs)
        # if no_of_jobs < 10:
        #     jobs = JobPost.objects.filter(status='Live')
        return jobs

    def get_recommended_jobposts(self):
        jobs = (
            JobPost.objects.filter(
                Q(skills__in=self.skills.all()) | Q(location__in=self.location.all())
            )
            .exclude(pk=self.id)
            .distinct()
        )
        jobs = (
            jobs.filter(status="Live")
            .select_related("company")
            .prefetch_related("location")
        )
        # no_of_jobs = len(jobs)
        # if no_of_jobs < 10:
        #     jobs = JobPost.objects.filter(status='Live')
        return jobs

    def get_locations(self):
        return self.location.values_list("name", flat=True)

    def get_job_type(self):
        if str(self.job_type) == "walk-in":
            return "walkin"
        elif str(self.job_type) == "Full_Time" or str(self.job_type) == "full_time":
            return "full-time"
        else:
            return self.job_type

    def get_active_skills(self):
        return self.skills.filter(status="Active").values_list("name", flat=True)

    def get_skills(self):
        return self.skills.filter().order_by("id")

    def get_active_functional_area(self):
        return self.functional_area.filter(status="Active").order_by("name")

    def get_active_qualification(self):
        return self.edu_qualification.filter(status="Active").order_by("name")

    def get_active_industries(self):
        return self.industry.filter(status="Active").order_by("name")

    def get_all_applied_users_count(self):
        return AppliedJobs.objects.filter(job_post=self).count()

    def get_selected_users(self):
        return AppliedJobs.objects.filter(job_post=self, status="Selected")

    def get_shortlisted_users(self):
        return AppliedJobs.objects.filter(job_post=self, status="Shortlisted")

    def get_rejected_users(self):
        return AppliedJobs.objects.filter(job_post=self, status="Rejected")

    def is_expired(self):
        current_date = datetime.strptime(
            str(datetime.now().date()), "%Y-%m-%d"
        ).strftime("%Y-%m-%d")
        if str(current_date) > str(self.last_date):
            return True
        else:
            return False

    def get_content(self):
        return ""

    def get_recruiter_assigned_jobposts(self):
        return AgencyRecruiterJobposts.objects.filter(job_post=self)

    def get_recruiter_hired_jobpost(self):
        return AgencyRecruiterJobposts.objects.filter(
            job_post=self, status="Hired"
        ).first()

    def get_hired_applicants(self):
        selected_applicants = AgencyApplicants.objects.filter(
            job_post=self, status="Hired"
        ).distinct()
        return selected_applicants

    def get_post_last_date(self):
        # today = arrow.utcnow().to('Asia/Calcutta').format('YYYY-MM-DD')
        current_date = datetime.strptime(str(self.last_date), "%Y-%m-%d").strftime(
            "%d %b %Y"
        )
        return current_date

    def get_post_created_date(self):
        # today = arrow.utcnow().to('Asia/Calcutta').format('YYYY-MM-DD')
        current_date = datetime.strptime(str(self.created_on), "%Y-%m-%d").strftime(
            "%d %b %Y"
        )
        return current_date

    def adding_applicants(self):
        job_post = self
        user_technical_skills = TechnicalSkill.objects.filter(
            skill__in=job_post.skills.all().values_list("id", flat=True)
        )
        users = User.objects.filter(user_type="JS", skills__in=user_technical_skills)
        for user in users:
            if not AppliedJobs.objects.filter(user=user, job_post=job_post):
                AppliedJobs.objects.create(
                    user=user,
                    job_post=job_post,
                    status="Pending",
                    ip_address="",
                    user_agent="",
                )

    def get_job_status(self):
        if self.status == "Disabled":
            return "inactive"
        return "active"

    def get_job_salary(self):
        if self.salary_type == "Month":
            return self.min_salary * 12, self.max_salary * 12
        else:
            return self.min_salary, self.max_salary

    def get_job_description(self):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(self.description)
        for s in soup(["script", "style"]):
            s.extract()
        return " ".join(soup.stripped_strings)

    def get_description(self):
        from bs4 import BeautifulSoup

        html = self.description
        # create a new bs4 object from the html data loaded
        soup = BeautifulSoup(html)
        # remove all javascript and stylesheet code
        for script in soup(["script", "style"]):
            script.extract()
        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text

    def get_company_emails(self):
        return self.company_emails

    def is_work_from_home(self):
        title = self.title.lower().replace(" ", "")
        if "workfromhome" in title or "parttime" in title:
            return True
        return False


POST = (
    ("Page", "Page"),
    ("Group", "Group"),
    ("PeelJobs", "PeelJobs"),
)

POST_STATUS = (
    ("Posted", "Posted"),
    ("Deleted", "Deleted"),
)

POST = (
    ("Page", "Page"),
    ("Profile", "Profile"),
    ("Group", "Group"),
    ("Profile", "Profile"),
)



POST_STATUS = (
    ("Pending", "Pending"),
    ("Shortlisted", "Shortlisted"),
    ("Hired", "Hired"),
    ("Rejected", "Rejected"),
)


class AgencyResume(models.Model):
    resume = models.CharField(max_length=5000, blank=True)
    candidate_name = models.CharField(max_length=1000)
    email = models.EmailField()
    mobile = models.CharField(max_length=100, blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)
    skill = models.ManyToManyField(Skill)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=POST, default="Pending")
    user = models.ForeignKey(
        User, blank=True, null=True, related_name="Applicant", on_delete=models.SET_NULL
    )
    created_on = models.DateTimeField(auto_now=True)


POST = (
    ("Pending", "Pending"),
    ("Shortlisted", "Shortlisted"),
    ("Selected", "Selected"),
    ("Rejected", "Rejected"),
    ("Process", "Process"),
)


class AppliedJobs(models.Model):
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(choices=POST_STATUS, max_length=50)
    applied_on = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=2000, default="")
    ip_address = models.CharField(max_length=2000, default="")
    user_agent = models.CharField(max_length=2000, default="")
    resume_applicant = models.ForeignKey(
        AgencyResume, null=True, blank=True, on_delete=models.CASCADE
    )


ENQUERY_TYPES = (
    ("Suggestion", "Suggestion"),
    ("Technical Issue", "Technical Issue"),
    ("Complaint", "Complaint"),
    ("others", "Others"),
)


class simplecontact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    comment = models.TextField()
    email = models.EmailField()
    phone = models.BigIntegerField(blank=True, null=True)
    contacted_on = models.DateField(auto_now=True)
    subject = models.CharField(max_length=500)
    enquery_type = models.CharField(max_length=100, choices=ENQUERY_TYPES)

    def __unicode__(self):
        return self.full_name


class MailTemplate(models.Model):
    message = models.TextField()
    subject = models.TextField()
    created_on = models.DateTimeField()
    modified_on = models.DateTimeField()
    title = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    show_recruiter = models.BooleanField(default=False)
    applicant_status = models.CharField(choices=POST_STATUS, max_length=50)


class SentMail(models.Model):
    send_on = models.DateTimeField(auto_now=True)
    recruiter = models.ManyToManyField(User)
    template = models.ForeignKey(MailTemplate, on_delete=models.CASCADE)
    job_post = models.ForeignKey(
        JobPost, null=True, blank=True, on_delete=models.CASCADE
    )


class JobAlert(models.Model):
    skill = models.ManyToManyField(Skill)
    location = models.ManyToManyField(City)
    min_year = models.IntegerField(null=True, blank=True)
    max_year = models.IntegerField(null=True, blank=True)
    max_salary = models.IntegerField(null=True, blank=True)
    min_salary = models.IntegerField(null=True, blank=True)
    industry = models.ManyToManyField(Industry)
    role = models.CharField(max_length=2000, blank=True, null=True)
    related_jobs = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=2000, unique=True)
    unsubscribe_code = models.CharField(max_length=100, null=True, blank=True)
    is_unsubscribe = models.BooleanField(default=False)
    subscribe_code = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    unsubscribe_reason = models.TextField(default="")


class SearchResult(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    job_post = models.CharField(max_length=1000, default=0)
    skills = models.ManyToManyField(Skill, related_name="skill_search")
    other_skill = models.CharField(max_length=1000)
    locations = models.ManyToManyField(City, related_name="location_search")
    other_location = models.CharField(max_length=1000)
    search_text = JSONField()
    industry = models.CharField(max_length=1000)
    search_on = models.DateTimeField(auto_now=True)
    functional_area = models.CharField(max_length=1000)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE, blank=True, null=True)
    expierence = models.IntegerField(blank=True, null=True)
    ip_address = models.CharField(max_length=200)


class Subscriber(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    job_post = models.ForeignKey(
        JobPost, blank=True, null=True, on_delete=models.SET_NULL
    )
    is_verified = models.BooleanField(default=False)
    unsubscribe_code = models.CharField(max_length=100, null=True, blank=True)
    is_unsubscribe = models.BooleanField(default=False)
    subscribe_code = models.CharField(max_length=100, null=True, blank=True)
    unsubscribe_reason = models.TextField(default="")

    def user_subscription_list(self):
        return Subscriber.objects.filter(email=self.email).exclude(id=self.id)


class VisitedJobs(models.Model):
    visited_on = models.DateTimeField(auto_now=True)
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Menu(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    lvl = models.IntegerField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


class DailySearchLog(models.Model):
    no_of_job_posts = models.IntegerField(default="0")
    skills = models.ForeignKey(Skill, on_delete=models.CASCADE)
    created_on = models.DateField()
    no_of_searches = models.IntegerField(default="0")


class AgencyApplicants(models.Model):
    applicant = models.ForeignKey(AgencyResume, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=POST, default="Pending")
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)


AGENCY_RECRUITER_JOB_TYPE = (
    ("Pending", "Pending"),
    ("Shortlisted", "Shortlisted"),
    ("Selected", "Selected"),
    ("Rejected", "Rejected"),
    ("Hired", "Hired"),
    ("Process", "Process"),
)


class AgencyRecruiterJobposts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=AGENCY_RECRUITER_JOB_TYPE, default="Pending"
    )
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)
    message = models.TextField(default="")


def skills_update(skill_slug, slug):
    removed_skill = Skill.objects.get(slug=skill_slug)
    job_posts = JobPost.objects.filter(skills__in=[removed_skill])
    latest_skill = Skill.objects.get(slug=slug)
    for i in job_posts:
        i.skills.add(latest_skill)
    removed_skill.delete()


class AgencyWorkLog(models.Model):
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    no_of_profiles = models.IntegerField()
    summary = models.TextField()
    timegap = models.CharField(max_length=100)


def updating_skills_jobposts(skill, update_skill):
    job_posts = JobPost.objects.filter(skills__in=[skill])
    for each in job_posts:
        each.skills.add(update_skill)
    skill.remove()


STATUS = (
    ("Pending", "Pending"),
    ("Live", "Live"),
    ("Closed", "Closed"),
)


class Solution(models.Model):
    description = models.TextField()
    given_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, max_length=20)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    attachments = models.ManyToManyField(Attachment)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def get_dislikes(self):
        dislikes = AssessmentData.objects.filter(
            solution=self, comment="", dislike=True
        )
        return dislikes

    def get_likes(self):
        likes = AssessmentData.objects.filter(solution=self, comment="", like=True)
        return likes

    def get_comments(self):
        comments = AssessmentData.objects.filter(solution=self).exclude(comment="")
        return comments


class Question(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills = models.ForeignKey(
        Skill, related_name="skill_questions", on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User, related_name="questions", blank=True, null=True, on_delete=models.CASCADE
    )
    solutions = models.ManyToManyField(Solution)
    status = models.CharField(choices=STATUS, max_length=20)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    attachments = models.ManyToManyField(Attachment)
    slug = models.SlugField(max_length=500)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    class Meta:
        unique_together = (
            "title",
            "skills",
        )
        ordering = ["-created_on"]

    def __unicode__(self):
        return self.title

    def get_dislikes(self):
        dislikes = AssessmentData.objects.filter(
            question=self, comment="", dislike=True
        )
        return dislikes

    def get_likes(self):
        likes = AssessmentData.objects.filter(question=self, comment="", like=True)
        return likes

    def get_solutions(self):
        solutions = self.solutions.filter(status="Live")
        return solutions

    def get_comments(self):
        comments = AssessmentData.objects.filter(question=self).exclude(comment="")
        return comments


class AssessmentData(models.Model):
    question = models.ForeignKey(
        Question, related_name="question_data", on_delete=models.CASCADE, null=True
    )
    solution = models.ForeignKey(
        Solution, related_name="solution_data", on_delete=models.CASCADE, null=True
    )
    user = models.ForeignKey(User, related_name="user_data", on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)
    comment = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)


# class CredentialsModel(models.Model):
#     id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
# credential = CredentialsField()


class MetaData(models.Model):
    name = models.CharField(max_length=2000)
    meta_title = models.CharField(max_length=2000)
    meta_description = models.CharField(max_length=2000)
    h1_tag = models.CharField(max_length=2000)


class UserMessage(models.Model):
    message = models.CharField(max_length=2000)
    message_from = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_messaged_from"
    )
    message_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_message_to"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(JobPost, null=True, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

