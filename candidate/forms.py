import re
from django import forms
from peeldb.models import User, EmploymentHistory, EducationDetails, Degree, EducationInstitue, Project, TechnicalSkill, JobAlert

SAL_TYPES = (
    ('Ms', 'Miss'),
    ('Mr', 'Mr'),
    ('Mrs', 'Mrs'),
    ('Dr', 'Dr'),
)
MAR_TYPES = (
    ('Married', 'Married'),
    ('Single', 'Single'),
)

DEGREE_TYPES = (
    ('Permanent', 'Permanent'),
    ('PartTime', 'PartTime'),
)

GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)


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


class PersonalInfoForm(forms.ModelForm):
    current_city = forms.CharField(max_length=50)
    preferred_city = forms.CharField(max_length=50, required=False)
    dob = forms.DateField(input_formats=('%m/%d/%Y',))
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30, required=False)
    marital_status = forms.CharField(max_length=30, required=False)
    pincode = forms.IntegerField(required=False)
    alternate_mobile = forms.IntegerField(required=False)
    resume_title = forms.CharField(max_length=2000, required=True)
    other_location = forms.CharField(required=False, error_messages={'required': "Other Location cannot be empty"})

    class Meta:
        model = User
        fields = ['first_name', 'mobile']

    def __init__(self, *args, **kwargs):
        super(PersonalInfoForm, self).__init__(*args, **kwargs)
        self.fields['current_city'].required = True
        self.fields['current_city'].error_messages = {'required': 'Current Location cannot be empty'}
        if 'other_loc' in self.data.keys():
            self.fields['current_city'].required = False
            self.fields['other_location'].required = True

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            users = User.objects.filter(mobile=mobile).exclude(id=self.instance.id)
            if not users:
                length = len(str(mobile)) < 10 or len(str(mobile)) > 12
                symbols = bool(re.search(r"[~\.,!@#\$%\^&\*\(\)_\{}\":;'\[\]]", mobile)) or bool(re.search('[a-zA-Z]', mobile))
                if length or symbols:
                    raise forms.ValidationError('Please Enter Valid phone number')
                if length or symbols:
                    raise forms.ValidationError('Please Enter Valid phone number')
                else:
                    return mobile
            else:
                raise forms.ValidationError('User with this mobile number already exists')

    def clean_alternate_mobile(self):
        form_cleaned_data = self.cleaned_data
        if form_cleaned_data['alternate_mobile']:
            if len(str(form_cleaned_data['alternate_mobile'])) < 10 or len(str(form_cleaned_data['alternate_mobile'])) > 12:
                raise forms.ValidationError(
                    'Please Enter Valid phone number')
            else:
                return form_cleaned_data['alternate_mobile']


class ProfessinalInfoForm(forms.ModelForm):
    prefered_industry = forms.CharField(max_length=50)
    year = forms.CharField(max_length=50)
    current_salary = forms.FloatField(required=False)
    expected_salary = forms.FloatField(required=False)

    class Meta:
        model = User
        fields = ['year', 'month', 'job_role']


class ProfileDescriptionForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['profile_description']


class WorkExperienceForm(forms.ModelForm):
    from_date = forms.DateField(input_formats=('%m/%d/%Y',))
    to_date = forms.DateField(required=True, input_formats=('%m/%d/%Y',))
    salary = forms.FloatField(required=False)

    class Meta:
        model = EmploymentHistory
        fields = ['company', 'from_date', 'designation', 'current_job']

    def __init__(self, *args, **kwargs):
        super(WorkExperienceForm, self).__init__(*args, **kwargs)
        if 'current_job' in self.data.keys():
            self.fields['to_date'].required = False

    def clean_to_date(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        if from_date and to_date and to_date < from_date:
            raise forms.ValidationError('To date Cannot be lesser than From Date')
        return to_date


class EducationForm(forms.ModelForm):
    from_date = forms.DateField(input_formats=('%m/%d/%Y',))
    to_date = forms.DateField(input_formats=('%m/%d/%Y',))
    score = forms.FloatField(required=False)

    class Meta:
        model = EducationDetails
        fields = ['from_date', 'current_education']

    def __init__(self, *args, **kwargs):
        super(EducationForm, self).__init__(*args, **kwargs)

        if self.data.get('current_education'):
            self.fields['to_date'].required = False

    def clean_to_date(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        if from_date and to_date and to_date < from_date:
            raise forms.ValidationError('To date Cannot be lesser than From Date')
        return to_date


class DegreeForm(forms.ModelForm):

    class Meta:
        model = Degree
        fields = ['degree_name', 'degree_type', 'specialization']


class EducationInstitueForm(forms.ModelForm):

    class Meta:
        model = EducationInstitue
        fields = ['name', 'city']


class ProjectForm(forms.ModelForm):
    from_date = forms.DateField(required=True, input_formats=('%m/%d/%Y',))
    to_date = forms.DateField(input_formats=('%m/%d/%Y',))

    class Meta:
        model = Project
        fields = ['name', 'from_date', 'to_date', 'description', 'skills', 'size', 'role']

    def clean_to_date(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        if from_date and to_date and to_date < from_date:
            raise forms.ValidationError('To date Cannot be lesser than From Date')
        return to_date


class TechnicalSkillForm(forms.ModelForm):
    is_major = forms.BooleanField(required=False)
    year = forms.IntegerField(required=True)
    month = forms.IntegerField(required=True)
    last_used = forms.DateField(required=False, input_formats=('%m/%d/%Y',))

    class Meta:
        model = TechnicalSkill
        fields = ['skill', 'year', 'month']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("requested_user", "")
        super(TechnicalSkillForm, self).__init__(*args, **kwargs)

        if 'is_major' in self.data.keys():
            self.fields['is_major'].required = True

    def clean_is_major(self):
        if 'is_major' in self.data.keys():
            if int(self.user.skills.filter(is_major=True).exclude(id=self.instance.id).count()) >= 2:
                raise forms.ValidationError(
                    'You need to provide only 2 major skills')
            else:
                return self.data['is_major']


class JobAlertForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    min_year = forms.IntegerField(required=False)
    max_year = forms.IntegerField(required=False)
    min_salary = forms.IntegerField(required=False)
    max_salary = forms.IntegerField(required=False)

    class Meta:
        model = JobAlert
        fields = ['name', 'skill', 'role']

    def __init__(self, *args, **kwargs):
        super(JobAlertForm, self).__init__(*args, **kwargs)
        if str(self.data.get('user_authenticated')) == 'True':
            self.fields['email'].required = False

        if self.data.get('min_year') or self.data.get('max_year'):
            self.fields['max_year'].required = True
            self.fields['min_year'].required = True

        if self.data.get('min_salary') or self.data.get('max_salary'):
            self.fields['max_salary'].required = True
            self.fields['min_salary'].required = True

    def clean_name(self):
        name = self.data.get('name', '')
        alerts = JobAlert.objects.filter(name__iexact=name).exclude(id=self.instance.id)
        if alerts.exists():
            raise forms.ValidationError("Alert Already Exists with This Name")
        return name

    def clean_max_salary(self):
        max_salary = self.cleaned_data.get('max_salary')
        if self.cleaned_data.get('min_salary') and max_salary:
            if int(max_salary) < int(self.cleaned_data.get('min_salary')):
                raise forms.ValidationError(
                    'Maximum salary must be greater than minimum salary'
                )
            return max_salary
        return max_salary
