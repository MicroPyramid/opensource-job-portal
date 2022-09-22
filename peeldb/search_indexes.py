from haystack import indexes
from peeldb.models import (
    JobPost,
    Skill,
    City,
    FunctionalArea,
    Industry,
    Qualification,
    State,
)
from datetime import datetime
from django.core import serializers
from mpcomp.views import get_absolute_url


class jobIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Indexing for job model
    """

    text = indexes.CharField(
        document=True, use_template=True, template_name="index/job_text.txt"
    )
    title = indexes.CharField(model_attr="title")
    designation = indexes.CharField(model_attr="job_role")
    job_type = indexes.CharField(model_attr="job_type", faceted=True)
    skills = indexes.MultiValueField()
    location = indexes.MultiValueField()
    slug = indexes.CharField(model_attr="slug")
    min_year = indexes.IntegerField(model_attr="min_year")
    max_year = indexes.IntegerField(model_attr="max_year")
    min_month = indexes.IntegerField(model_attr="min_month")
    max_month = indexes.IntegerField(model_attr="max_month")
    min_salary = indexes.FloatField()
    max_salary = indexes.FloatField()
    industry = indexes.MultiValueField()
    edu_qualification = indexes.MultiValueField()
    functional_area = indexes.MultiValueField()
    walkin_from_date = indexes.DateField(null=True, model_attr="walkin_from_date")
    walkin_to_date = indexes.DateField(null=True, model_attr="walkin_to_date")
    status = indexes.CharField(model_attr="status")
    # posted_on = indexes.DateField(model_attr='posted_on')
    created_on = indexes.DateField(model_attr="created_on")
    description = indexes.CharField(model_attr="description")
    post_url = indexes.CharField()
    company_name = indexes.CharField(model_attr="company_name")
    company = indexes.CharField(model_attr="company", null=True)
    published_on = indexes.DateField(model_attr="published_on", null=True)

    def get_model(self):
        return JobPost

    def prepare_post_url(self, obj):
        return get_absolute_url(obj)

    def prepare_skills(self, obj):
        return [str(s.name) for s in obj.skills.filter(status="Active")]

    def prepare_location(self, obj):
        locations = serializers.serialize("json", obj.location.all())
        return locations

    def prepare_industry(self, obj):
        return [str(s.name) for s in obj.industry.all()]

    def prepare_functional_area(self, obj):
        return [str(l.name) for l in obj.functional_area.all()]

    def prepare_min_salary(self, obj):
        if int(obj.min_salary) > 0:
            return float(obj.min_salary) / 100000
        else:
            return 0.0

    def prepare_max_salary(self, obj):
        if int(obj.max_salary) > 0:
            return float(obj.max_salary) / 100000
        else:
            return 0.0

    def prepare_created_on(self, obj):
        if obj.created_on:
            current_date = datetime.strptime(str(obj.created_on), "%Y-%m-%d").strftime(
                "%Y-%m-%d"
            )
            return current_date
        return None

    def prepare_published_on(self, obj):
        if obj.published_on:
            current_date = datetime.strptime(
                str(obj.published_on.date()), "%Y-%m-%d"
            ).strftime("%Y-%m-%d")
            return current_date
        return None

    def prepare_edu_qualification(self, obj):
        return [str(s.name) for s in obj.edu_qualification.filter(status="Active")]

    # def prepare_walkin_from_date(self, obj):
    #     if obj.walkin_from_date:
    #         current_date = datetime.strptime(str(obj.walkin_from_date), "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
    #         return current_date
    #     return None

    # def prepare_walkin_to_date(self, obj):
    #     if obj.walkin_to_date:
    #         current_date = datetime.strptime(str(obj.walkin_to_date), "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
    #         return current_date
    #     return None

    def index_queryset(self, using=None):
        # from datetime import datetime
        # current_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").strftime("%Y-%m-%d")
        return (
            self.get_model()
            .objects.filter(status="Live")
            .select_related("company", "user")
            .prefetch_related(
                "location", "edu_qualification", "industry", "skills", "functional_area"
            )
        )


class skillautoIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Index for autocompleate for designation and skills
    """

    text = indexes.CharField(
        document=True, use_template=True, template_name="index/skill_text.txt"
    )
    skill_name = indexes.CharField(model_attr="name")
    skill_slug = indexes.CharField(model_attr="slug")
    no_of_jobposts = indexes.CharField()
    status = indexes.CharField(model_attr="status")

    def get_model(self):
        return Skill

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(status="Active")

    def prepare_no_of_jobposts(self, obj):
        return obj.get_no_of_jobposts().count()


class locationIndex(indexes.SearchIndex, indexes.Indexable):
    """index for loacation"""

    text = indexes.CharField(
        document=True, use_template=True, template_name="index/city_text.txt"
    )
    city_name = indexes.CharField(model_attr="name")
    no_of_jobposts = indexes.CharField()
    status = indexes.CharField(model_attr="status")

    def get_model(self):
        return City

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(status="Enabled")

    def prepare_no_of_jobposts(self, obj):
        return obj.get_no_of_jobposts().count()


class industryIndex(indexes.SearchIndex, indexes.Indexable):
    """index for loacation"""

    text = indexes.CharField(
        document=True, use_template=True, template_name="index/industry_text.txt"
    )
    industry_name = indexes.CharField(model_attr="name")
    no_of_jobposts = indexes.CharField()
    industry_slug = indexes.CharField(model_attr="slug")

    def get_model(self):
        return Industry

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_no_of_jobposts(self, obj):
        return obj.get_no_of_jobposts().count()


class functionalareaIndex(indexes.SearchIndex, indexes.Indexable):
    """index for loacation"""

    text = indexes.CharField(
        document=True, use_template=True, template_name="index/functionalarea_text.txt"
    )
    functionalarea_name = indexes.CharField(model_attr="name")
    no_of_jobposts = indexes.CharField()

    def get_model(self):
        return FunctionalArea

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_no_of_jobposts(self, obj):
        return obj.get_no_of_jobposts().count()


class qualificationIndex(indexes.SearchIndex, indexes.Indexable):
    """index for loacation"""

    text = indexes.CharField(
        document=True, use_template=True, template_name="index/qualification_text.txt"
    )
    edu_name = indexes.CharField(model_attr="name")
    edu_slug = indexes.CharField(model_attr="slug")
    no_of_jobposts = indexes.CharField()

    def get_model(self):
        return Qualification

    def prepare_no_of_jobposts(self, obj):
        return obj.get_no_of_jobposts().count()

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(status="Active")


class stateIndex(indexes.SearchIndex, indexes.Indexable):
    """index for State"""

    text = indexes.CharField(
        document=True, use_template=True, template_name="index/state_text.txt"
    )
    state_name = indexes.CharField(model_attr="name")
    no_of_cities = indexes.CharField()
    status = indexes.CharField(model_attr="status")
    no_of_jobposts = indexes.CharField()
    is_duplicate = indexes.BooleanField(default=False)

    def get_model(self):
        return State

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(status="Enabled")

    def prepare_no_of_cities(self, obj):
        return obj.state.all().count()

    def prepare_no_of_jobposts(self, obj):
        return obj.get_no_of_jobposts().count()

    def prepare_is_duplicate(self, obj):
        return obj.state.filter(name=obj.name).exists()
