import re

from django import forms
from django.forms.models import ModelForm
from datetime import datetime

from peeldb.models import (Company, User, JobPost, MailTemplate, Menu, AgencyCompany, \
                           AgencyResume, AgencyApplicants, AgencyWorkLog)
from django.contrib.auth.hashers import check_password
from mpcomp.views import get_asia_time, custom_password_check


class Company_Form(forms.ModelForm):
    name = forms.CharField(max_length=100, error_messages={'required': 'Company Name can not be blank'})
    website = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Company
        fields = ['name', 'website']

    def __init__(self, *args, **kwargs):
        super(Company_Form, self).__init__(*args, **kwargs)

    def clean_name(self):
        companies = Company.objects.filter(name__iexact=self.data['name']).exclude(id=self.instance.id)
        if companies:
            users = User.objects.filter(company__in=companies.values_list('id', flat=True), is_admin=True)
            if users:
                raise forms.ValidationError('Company with this name already exists')
        return self.data['name']

    def clean_website(self):
        if self.data['website']:
            if (
                    re.match(r'^http://', self.data['website']) or
                    re.match(r'^https://', self.data['website']) or
                    re.match(r'^www.', self.data['website'])):
                if self.cleaned_data['website']:
                    companies = Company.objects.filter(website__iexact=self.data['website']).exclude(id=self.instance.id)
                    if companies:
                        users = User.objects.filter(company__in=companies.values_list('id', flat=True), is_admin=True)
                        if users:
                            raise forms.ValidationError(
                                'Company with this website already exists')
                return self.data['website']
            else:
                raise forms.ValidationError(
                    'Please include website with http:// or https:// or www.')
        return self.data['website']

    def save(self, commit=True):
        instance = super(Company_Form, self).save(commit=False)
        instance.name = self.cleaned_data['name']
        instance.website = self.cleaned_data['website']
        instance.company_type = self.cleaned_data['company_type']
        if commit:
            instance.save()
        return instance


class User_Form(forms.ModelForm):
    password = forms.CharField(
        max_length=50, error_messages={'required': 'Password can not be blank'})
    email = forms.CharField(max_length=50, error_messages={
                            'required': 'Email can not be blank', 'invalid': 'Please enter a valid email'})
    mobile = forms.CharField(error_messages={
                                'required': 'Phone Number can not be blank', 'invalid': 'Please enter a valid phone number'})
    client_type = forms.CharField(
        max_length=50, error_messages={'required': 'Please select your choice'})
    username = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ['mobile', 'email', 'username']

    def clean_email(self):
        user = User.objects.filter(email__iexact=self.data['email']).exclude(id=self.instance.id)
        if user.exists():
            raise forms.ValidationError("User Already Exists as " + user[0].get_user_type_display())
        return self.data['email']

    def clean_password(self):
        if self.data['password']:
            msg = custom_password_check(self.data['password'])
            if msg:
                raise forms.ValidationError(msg)
            else:
                return self.data['password']
        raise forms.ValidationError('Password can not be blank')

    def clean_mobile(self):
        mobile = self.data['mobile']
        if mobile:
            users = User.objects.filter(mobile=mobile)
            if not users:
                length = len(str(mobile)) < 10 or len(str(mobile)) > 12
                symbols = bool(re.search(r"[~\.,!@#\$%\^&\*\(\)_\{}\":;'\[\]]", mobile)) or bool(re.search('[a-zA-Z]', mobile))
                if length or symbols:
                    raise forms.ValidationError('Please Enter Valid phone number')
                else:
                    return self.data['mobile']
            else:
                raise forms.ValidationError(
                    'User with this mobile number already exists')
        else:
            raise forms.ValidationError('Phone Number can not be blank')

    def clean_username(self):
        username = self.data.get('username', '')
        if bool(re.search(r"[~\!@#\$%\^&\*\(\)\+{}\":;,=._'/ >?|<\\[\]]", username)):
            raise forms.ValidationError("Username Should not contain spaces and any special characters")
        return username


class ChangePasswordForm(forms.Form):
    oldpassword = forms.CharField(max_length=50, error_messages={
                                  'required': 'Please enter your current password', 'invalid': 'Enter a valid email'})
    newpassword = forms.CharField(max_length=50, error_messages={
                                  'required': 'Please enter new password', 'invalid': 'Enter a valid email'})
    retypepassword = forms.CharField(max_length=50, error_messages={
                                     'required': 'Please enter confirm password', 'invalid': 'Enter a valid email'})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_oldpassword(self):
        if not check_password(self.data['oldpassword'], self.user.password):
            raise forms.ValidationError(
                'Please enter your old password correctly')
        else:
            return self.data['oldpassword']

    def clean_newpassword(self):
        if self.data['newpassword'] != self.data['retypepassword']:
            raise forms.ValidationError(
                'New password and Confirm password should match')
        else:
            return self.data['newpassword']


class PersonalInfoForm(forms.ModelForm):
    dob = forms.DateField(required=False, input_formats=('%m/%d/%Y',))
    first_name = forms.CharField(max_length=30)
    city = forms.CharField(max_length=50)
    state = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=30)
    mobile = forms.CharField(required=True)
    year = forms.IntegerField(required=True)
    month = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'nationality', 'mobile',
                  'technical_skills', 'industry', 'functional_area', 'year', 'month',
                  'profile_description', 'job_role']

    def __init__(self, *args, **kwargs):
        super(PersonalInfoForm, self).__init__(*args, **kwargs)
        if 'dob' in self.data.keys() and self.data['dob']:
            self.fields['dob'].required = True

    def clean_mobile(self):
        users = User.objects.filter(mobile=self.data['mobile']).exclude(id=int(self.data['user_id']))
        mobile = str(self.data['mobile'])
        if not users:
            length = len(mobile) < 10 or len(mobile) > 12
            symbols = bool(re.search(r"[~\.,!@#\$%\^&\*\(\)_\{}\":;'\[\]]", mobile)) or bool(re.search('[a-zA-Z]', mobile))
            if length or symbols:
                raise forms.ValidationError('Please Enter Valid phone number')
            else:
                return mobile
        else:
            raise forms.ValidationError(
                'User with this mobile number already exists')


class MobileVerifyForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['mobile_verification_code']


YEARS = (
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
        ('14', '14'),
        ('15', '15'),
        ('16', '16'),
        ('17', '17'),
        ('18', '18'),
        ('19', '19'),
        ('20', '20'),

)


MONTHS = (
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
)

valid_time_formats = ['%H:%M', '%I:%M%p', '%I:%M %p']


class JobPostForm(ModelForm):

    min_salary = forms.IntegerField(required=False)
    max_salary = forms.IntegerField(required=False)
    published_date = forms.DateTimeField(
        input_formats=('%m/%d/%Y %H:%M:%S',), required=False)
    walkin_contactinfo = forms.CharField(max_length=10000, required=False)
    walkin_from_date = forms.DateField(required=False, input_formats=('%m/%d/%Y',))
    walkin_to_date = forms.DateField(required=False, input_formats=('%m/%d/%Y',))
    walkin_time = forms.TimeField(
        required=False, input_formats=valid_time_formats)
    vacancies = forms.IntegerField(required=False)
    company_description = forms.CharField(max_length=10000)
    application_fee = forms.IntegerField(required=False)
    selection_process = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Please enter the  selection process'}), required=False)
    how_to_apply = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Please enter the  selection process'}), required=False)
    important_dates = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Please enter the  selection process'}), required=False)
    govt_from_date = forms.DateField(required=False, input_formats=('%m/%d/%Y',))
    govt_to_date = forms.DateField(required=False, input_formats=('%m/%d/%Y',))
    govt_exam_date = forms.DateField(required=False, input_formats=('%m/%d/%Y',))
    age_relaxation = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Please enter the  selection process'}), required=False)
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
        exclude = ['user', 'code', 'country', 'status', 'previous_status', 'fb_views', 'tw_views', 'ln_views',
                   'other_views', 'fb_groups', 'post_on_fb', 'post_on_tw',
                   'post_on_ln', 'keywords', 'job_interview_location', 'job_type', 'govt_job_type',
                   'agency_client', 'company', 'meta_title', 'meta_description', 'agency_category', 'major_skill', 'vacancies', 'slug']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(JobPostForm, self).__init__(*args, **kwargs)

        if self.user.is_superuser:
            self.fields['company'].required = True
            self.fields['company_address'].required = False
            self.fields['company_name'].required = False
            self.fields['company_description'].required = False
            self.fields['company_website'].required = False

        if self.user.company and self.user.is_agency_recruiter:
            # self.fields['code'].required = False
            self.fields['agency_job_type'].required = True
            self.fields['agency_recruiters'].required = True
        else:
            self.fields['agency_recruiters'].required = False

        if 'vacancies' in self.data.keys() and self.data['vacancies']:
            self.fields['vacancies'].required = True

        if 'salary_type' in self.data.keys() and self.data['salary_type']:
            self.fields['max_salary'].required = True
            self.fields['min_salary'].required = True

        if 'min_salary' in self.data.keys() and self.data['min_salary'] or 'max_salary' in self.data.keys() and self.data['max_salary']:
            self.fields['salary_type'].required = True

        if 'min_salary' in self.data.keys() and self.data['min_salary']:
            self.fields['salary_type'].required = True
            self.fields['min_salary'].required = True
        if 'max_salary' in self.data.keys() and self.data['max_salary']:

            self.fields['max_salary'].required = True
            self.fields['salary_type'].required = True

        if 'final_industry' in self.data.keys():
            if len(self.data['final_industry']) > 2:
                self.fields['industry'].required = False
            else:
                self.fields['industry'].required = True
        if 'final_skills' in self.data.keys():
            if len(self.data['final_skills']) > 2:
                self.fields['skills'].required = False
            else:
                self.fields['skills'].required = True
        if 'final_edu_qualification' in self.data.keys():
            if len(self.data['final_edu_qualification']) > 2:
                self.fields['edu_qualification'].required = False
            else:
                self.fields['edu_qualification'].required = True
        if 'final_functional_area' in self.data.keys():
            if len(self.data['final_functional_area']) > 2:
                self.fields['functional_area'].required = False
            else:
                self.fields['functional_area'].required = True
        if 'other_location' in self.data.keys():
            if len(self.data['other_location']) != 0:
                self.fields['location'].required = False

        if 'visa_required' in self.data.keys() and self.data['visa_required']:
            self.fields['visa_country'].required = True
            self.fields['visa_type'].required = True
        else:
            self.fields['visa_country'].required = False
            self.fields['visa_type'].required = False

        if str(self.data['job_type']) == 'walk-in':
            self.fields['walkin_contactinfo'].required = True
            self.fields['walkin_from_date'].required = True
            self.fields['walkin_to_date'].required = True
            self.fields['walkin_time'].required = True
            self.fields['vacancies'].required = False
            # self.fields['company_description'].required = False
            self.fields['industry'].required = False
            self.fields['skills'].required = False
            self.fields['functional_area'].required = False
            self.fields['last_date'].required = False
            # self.fields['code'].required = False
            self.fields['job_role'].required = False
            self.fields['company_description'].required = False
            self.fields['walkin_time'].required = False
            self.fields['edu_qualification'].required = False

        if str(self.data['job_type']) == 'government':

            self.fields['min_year'].required = False
            self.fields['max_year'].required = False
            self.fields['min_month'].required = False
            self.fields['max_month'].required = False
            self.fields['company_address'].required = False

            self.fields['application_fee'].required = False
            self.fields['selection_process'].required = False
            self.fields['how_to_apply'].required = True
            self.fields['important_dates'].required = True
            self.fields['age_relaxation'].required = True
            self.fields['govt_from_date'].required = True
            self.fields['govt_to_date'].required = True
            self.fields['govt_exam_date'].required = False

            self.fields['industry'].required = False
            self.fields['skills'].required = False
            self.fields['functional_area'].required = False
            self.fields['last_date'].required = False
            # self.fields['code'].required = False
            self.fields['job_role'].required = False
            self.fields['company_description'].required = False

        if str(self.data['job_type']) == 'full-time':
            self.fields['last_date'].required = False
            self.fields['edu_qualification'].required = False

        if str(self.data['job_type']) == 'internship':
            self.fields['last_date'].required = False
            self.fields['edu_qualification'].required = False

    def clean_title(self):
        title = self.cleaned_data['title']
        if bool(re.search(r"[~\.,!@#\$%\^&\*\(\)_\+{}\":;'\[\]\<\>\|\/]", title)) or bool(re.search(r"[0-9]", title)):
            raise forms.ValidationError("Title Should not contain special charecters and numbers")
        if JobPost.objects.filter(title=title).exclude(id=self.instance.id):
            raise forms.ValidationError("Job Post with this title already exists")
        return title.replace('/', '-')

    def clean_vacancies(self):
        if 'vacancies' in self.data.keys() and self.data['vacancies']:
            if int(self.data['vacancies']) <= 0:
                raise forms.ValidationError('Vacancies must be greater than zero')
            else:
                return self.cleaned_data.get('vacancies')
        return self.cleaned_data.get('vacancies')

    def clean_last_date(self):
        date = self.cleaned_data['last_date']
        if str(date) < str(datetime.now().date()):
            raise forms.ValidationError("The date cannot be in the past!")
        return date

    def clean_govt_exam_date(self):
        if ('govt_exam_date', 'govt_from_date', 'govt_to_date') in self.data.keys():
            date = self.cleaned_data['govt_exam_date']
            from_date = self.data['govt_from_date']
            to_date = self.data['govt_to_date']
            if (date and from_date and to_date):
                to_date = datetime.strptime(
                    str(to_date), "%m/%d/%Y").strftime("%Y-%m-%d")
                from_date = datetime.strptime(
                    str(from_date), "%m/%d/%Y").strftime("%Y-%m-%d")

                if str(date) < str(datetime.now().date()):
                    raise forms.ValidationError(
                        "The date cannot be in the past!")
                if str(from_date) > str(date) or str(to_date) > str(date):
                    raise forms.ValidationError(
                        "Exam Date must be in between from and to date")
                return date

    def clean_govt_from_date(self):
        if 'govt_from_date' in self.data.keys():
            date = self.cleaned_data['govt_from_date']
            if str(date) < str(datetime.now().date()):
                raise forms.ValidationError("The date cannot be in the past!")
            return date

    def clean_govt_to_date(self):
        if 'govt_to_date' in self.data.keys():
            date = self.cleaned_data['govt_to_date']
            if str(date) < str(datetime.now().date()):
                raise forms.ValidationError("The date cannot be in the past!")
            from_date = self.data['govt_from_date']
            from_date = datetime.strptime(
                str(from_date), "%m/%d/%Y").strftime("%Y-%m-%d")
            if str(from_date) > str(date):
                raise forms.ValidationError(
                    "To Date must be greater than From Date")
            return date

    def clean_published_date(self):
        date_time = self.cleaned_data['published_date']
        asia_time = get_asia_time()
        if date_time:
            if str(date_time) < str(asia_time):
                raise forms.ValidationError('The date cannot be in the past!')
            if str(self.data['job_type']) == 'walk-in':
                if 'walkin_to_date' in self.cleaned_data.keys() and self.cleaned_data['walkin_to_date'] > date_time.date():
                    return date_time
                else:
                    raise forms.ValidationError(
                        'Published date must be less than walkin end date')
            return date_time

    def clean_min_salary(self):
        if self.cleaned_data.get('min_salary'):
            try:
                min_sal = int(self.cleaned_data['min_salary'])
                return min_sal
            except:
                raise forms.ValidationError('Minimum salary must be an Integer')
        else:
            return 0

    def clean_max_salary(self):
        if self.cleaned_data.get('min_salary') and self.cleaned_data.get('max_salary'):
            if int(self.cleaned_data['max_salary']) < int(self.cleaned_data['min_salary']):
                raise forms.ValidationError('Maximum salary must be greater than minimum salary')
            return self.cleaned_data['max_salary']
        elif self.cleaned_data.get('max_salary'):
            return self.cleaned_data['max_salary']
        return 0

    def clean_company_name(self):
        # companies = Company.objects.filter(name__iexact=self.data['company_name'])
        # if self.instance.company:
        #     companies = companies.exclude(id=self.instance.company.id)
        # if companies:
        #     raise forms.ValidationError('Company with this name already exists')
        return self.data['company_name']

    def clean_company_website(self):
        if 'company_website' in self.data and self.data['company_website']:
            if (
                    re.match(r'^http://', self.data['company_website']) or
                    re.match(r'^https://', self.data['company_website']) or
                    re.match(r'^www.', self.data['company_website'])):

                company = ''
                if 'company_id' in self.data.keys() and self.data['company_id']:
                    company = Company.objects.filter(
                        id=self.data['company_id'])
                if company:
                    companies = Company.objects.filter(
                        website__iexact=self.data['company_website']).exclude(id=self.data['company_id'])
                    if companies:
                        raise forms.ValidationError('Company with this website already exists')
                return self.cleaned_data['company_website']
            else:
                raise forms.ValidationError('Please include website with http:// or https:// or www.')

    def clean_company_logo(self):
        company_logo = self.cleaned_data.get('company_logo')
        if company_logo:
            sup_formates = ["image/jpeg", 'image/png']
            ftype = company_logo.content_type
            if str(ftype) not in sup_formates:
                raise forms.ValidationError("Please upload Valid Image Format Ex: PNG, JPEG, JPG")
            return company_logo
        return company_logo

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode:
            match = re.findall(r"\d{6}", pincode)
            if not match or len(pincode) != 6:
                raise forms.ValidationError('Please Enter 6 digit valid Pincode')
        return pincode


class MailTemplateForm(ModelForm):

    recruiters = forms.CharField(max_length=1000, required=False)

    class Meta:
        model = MailTemplate
        fields = ['subject', 'message', 'title']

    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)
        if 'mode' in self.data.keys() and self.data['mode'] == 'send_mail':
            self.fields['recruiters'].required = True

    def clean_subject(self):
        if len(self.data['subject']) > 100:
            raise forms.ValidationError(
                'Subject is too long, we expect it to be less than 100 characters')
        else:
            return self.data['subject']

    def clean_message(self):
        if len(self.data['message']) > 200000:
            raise forms.ValidationError(
                'Mail is too big, please try with simple matter!')
        else:
            return self.data['message']


class EditCompanyForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = Company
        fields = ['name', 'website', 'profile', 'address', 'level']

    def __init__(self, *args, **kwargs):
        super(EditCompanyForm, self).__init__(*args, **kwargs)

    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get('profile_pic')
        if profile_pic:
            sup_formates = ["image/jpeg", 'image/png']
            ftype = profile_pic.content_type
            if str(ftype) not in sup_formates:
                raise forms.ValidationError("Please upload Valid Image Format Ex: PNG, JPEG, JPG")
            return self.cleaned_data['profile_pic']
        return profile_pic

    def clean_website(self):
        if self.cleaned_data['website']:
            if (re.match(r'^http://', self.cleaned_data['website']) or
                    re.match(r'^https://',  self.cleaned_data['website']) or
                    re.match(r'^www.', self.cleaned_data['website'])):
                return self.cleaned_data['website']
            else:
                raise forms.ValidationError(
                    "Please include website with http:// or https:// or www.")
        return self.cleaned_data['website']

    def clean_name(self):
        companies = Company.objects.filter(
            name__iexact=self.data['name']).exclude(id=self.instance.id)
        if companies:
            users = User.objects.filter(
                company__in=companies.values_list('id', flat=True), is_admin=True)
            if users:
                raise forms.ValidationError(
                    'Company with this name already exists')
        return self.data['name']


class RecruiterForm(forms.ModelForm):
    password = forms.CharField(max_length=100)
    profile_pic = forms.ImageField(required=False)
    first_name = forms.CharField(max_length=50)


    class Meta:
        model = User
        fields = ['mobile', 'email', 'job_role', 'profile_pic', 'first_name']

    def clean_password(self):
        if self.data['password']:
            msg = custom_password_check(self.data['password'])
            if msg:
                raise forms.ValidationError(msg)
            else:
                return self.data['password']
        raise forms.ValidationError('Password can not be blank')

    def clean_email(self):
        users = User.objects.filter(
            email=self.data['email']).exclude(id=self.instance.id)
        if not users:
            return self.data['email']
        else:
            raise forms.ValidationError('User with this email already exists')

    def clean_mobile(self):
        mobile = str(self.data['mobile'])
        if mobile:
            users = User.objects.filter(mobile=mobile).exclude(id=self.instance.id)
            if not users:
                length = len(mobile) < 10 or len(mobile) > 12
                symbols = bool(re.search(r"[~\.,!@#\$%\^&\*\(\)_\{}\":;'\[\]]", mobile)) or bool(re.search('[a-zA-Z]', mobile))
                if length or symbols:
                    raise forms.ValidationError('Please Enter Valid phone number')
            else:
                raise forms.ValidationError(
                    'User with this mobile number already exists')
            return mobile
        else:
            raise forms.ValidationError('This Field is required')

    def clean_profile_pic(self):
        if self.files or self.instance.profile_pic:
            return self.cleaned_data['profile_pic']


class MenuForm(forms.ModelForm):

    class Meta:
        model = Menu
        fields = ['title', 'url']


class ClientForm(forms.ModelForm):
    logo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ClientForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AgencyCompany
        fields = ['name', 'website', 'decription']

    def clean_name(self):
        companies = AgencyCompany.objects.filter(
            name=self.data['name'], website=self.data['website']).exclude(id=self.instance.id)
        if not companies:
            return self.data['name']
        else:
            raise forms.ValidationError(
                'Client with this name, website already exists')


class ResumeUploadForm(forms.ModelForm):
    resume = forms.FileField()
    skill = forms.CharField(max_length=1000)
    email = forms.EmailField()
    mobile = forms.CharField(required=False)
    experience = forms.IntegerField(required=False)
    status = forms.CharField(required=False)
    job_post = forms.CharField(required=False)

    class Meta:
        model = AgencyResume
        fields = ['candidate_name', 'mobile', 'experience']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ResumeUploadForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['resume'].required = False
        if 'job_post' in self.data.keys() and self.data['job_post']:
            self.fields['job_post'].required = True
            self.fields['status'].required = True

    def clean_mobile(self):
        if self.data['mobile']:
            users = AgencyResume.objects.filter(
                mobile=self.data['mobile'], uploaded_by=self.request.user).exclude(id=self.instance.id)
            if not users:
                if len(str(self.data['mobile'])) < 10 or len(str(self.data['mobile'])) > 12:
                    raise forms.ValidationError(
                        'Please Enter Valid phone number')
                else:
                    return self.data['mobile']
            else:
                raise forms.ValidationError(
                    'User with this mobile number already exists')
        return

    def clean_email(self):
        if self.request.user.email == self.data['email']:
            raise forms.ValidationError('User with this Email already exists')
        users = AgencyResume.objects.filter(
            email=self.data['email'], uploaded_by=self.request.user).exclude(id=self.instance.id)
        if not users:
            return self.data['email']
        else:
            raise forms.ValidationError('User with this Email already exists')


class ApplicantResumeForm(forms.ModelForm):

    class Meta:
        model = AgencyApplicants
        fields = ['status', 'job_post']


class AgencyWorkLogForm(forms.ModelForm):

    class Meta:
        model = AgencyWorkLog
        fields = ['job_post', 'user', 'start_time', 'end_time', 'summary', 'no_of_profiles']


choices = [('Process', "Process"),
           ('Pending', "Pending"),
           ('Selected', "Selected"),
           ('Shortlisted', "Shortlisted"),
           ('Rejected', "Rejected")
           ]


class UserStatus(forms.Form):
    status = forms.ChoiceField(choices=choices)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        if user.user:
            user_id = user.user.id
        else:
            user_id = user.resume_applicant.id
        super(UserStatus, self).__init__(*args, **kwargs)
        self.fields['status'].initial = user.status
        self.fields['status'].widget.attrs.update({'id': 'user_status_' + str(user_id),
                                                   'class': 'user_status'})
