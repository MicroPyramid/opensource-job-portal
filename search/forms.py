import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

from django import forms
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet, SQ

from peeldb.models import City

VALID_TIME_FORMATS = ["%Y-%m-%d 00:00:00"]


class JobSearchForm(SearchForm):
    """Search form for filtering and query building on job listings."""

    q = forms.CharField(max_length=200, required=False)
    location = forms.CharField(required=False)
    experience = forms.IntegerField(required=False)
    salary = forms.IntegerField(required=False)
    job_type = forms.CharField(required=False)
    industry = forms.CharField(required=False)
    functional_area = forms.CharField(required=False)
    walkin_from_date = forms.DateField(required=False)
    walkin_to_date = forms.DateField(required=False)
    walkin_type = forms.CharField(required=False)
    refine_location = forms.CharField(required=False)

    def search(self):
        """
        Build and return the search query based on form input.

        The search query filters live job posts and then applies
        additional filters based on the form's cleaned_data.
        """
        sqs = SearchQuerySet().filter_and(status="Live")
        if not self.is_valid():
            return sqs

        query = self.cleaned_data.get("q")
        location_field = self.cleaned_data.get("location")
        if query and location_field:
            # Process basic query filters.
            term = query.replace("[", "").replace("]", "").replace("'", "")
            terms = [t.strip() for t in term.split(",") if t.strip()]
            sqs = sqs.filter_and(
                SQ(title__in=terms) | SQ(designation__in=terms) | SQ(skills__in=terms)
            )

            loc = location_field.replace("[", "").replace("]", "").replace("'", "")
            locations = [t.strip() for t in loc.split(",") if t.strip()]
            other_cities = City.objects.filter(name__in=locations).values_list(
                "parent_city__name", flat=True
            )
            sqs = sqs.filter_and(
                SQ(location__in=locations)
                | SQ(location__startswith=location_field)
                | SQ(location__in=other_cities)
            )

            if self.cleaned_data.get("job_type"):
                sqs = sqs.filter_and(job_type=self.cleaned_data["job_type"])

            if self.cleaned_data.get("industry"):
                industry_value = self.cleaned_data["industry"]
                industries = [t.strip() for t in industry_value.split(",") if t.strip()]
                sqs = sqs.filter_or(industry__in=industries)

            if self.cleaned_data.get("functional_area"):
                fa_value = self.cleaned_data["functional_area"]
                functional_areas = [
                    t.strip() for t in fa_value.split(",") if t.strip()
                ]
                sqs = sqs.filter_or(functional_area__in=functional_areas)

            if self.cleaned_data.get("experience") is not None:
                experience_val = self.cleaned_data["experience"]
                sqs = sqs.filter_or(
                    SQ(max_experience__gte=experience_val)
                    & SQ(min_experience__lte=experience_val)
                )

            if self.cleaned_data.get("salary") is not None:
                salary_val = self.cleaned_data["salary"]
                sqs = sqs.filter_or(
                    SQ(max_salary__gte=salary_val)
                    & SQ(min_salary__lte=salary_val)
                )

            walkin_type = self.cleaned_data.get("walkin_type")
            if walkin_type:
                if walkin_type == "this_week":
                    today = date.today()
                    start_week = today - datetime.timedelta(today.weekday()) - datetime.timedelta(1)
                    end_week = start_week + datetime.timedelta(6)
                    start_str = start_week.strftime("%Y-%m-%d")
                    end_str = end_week.strftime("%Y-%m-%d")
                    sqs = sqs.filter_and(
                        SQ(walkin_from_date__range=[start_str, end_str])
                        | SQ(walkin_to_date__range=[start_str, end_str])
                    )
                elif walkin_type == "next_week":
                    today = date.today()
                    start_week = today - datetime.timedelta(today.isoweekday()) + datetime.timedelta(7)
                    end_week = start_week + datetime.timedelta(6)
                    start_str = start_week.strftime("%Y-%m-%d")
                    end_str = end_week.strftime("%Y-%m-%d")
                    sqs = sqs.filter_and(
                        SQ(walkin_from_date__range=[start_str, end_str])
                        | SQ(walkin_to_date__range=[start_str, end_str])
                    )
                elif walkin_type == "this_month":
                    current_date = date.today()
                    start_month = date(current_date.year, current_date.month, 1)
                    end_month = start_month + relativedelta(day=31)
                    start_str = start_month.strftime("%Y-%m-%d")
                    end_str = end_month.strftime("%Y-%m-%d")
                    sqs = sqs.filter_and(
                        SQ(walkin_from_date__range=[start_str, end_str])
                        | SQ(walkin_to_date__range=[start_str, end_str])
                    )
                elif walkin_type == "custom_range":
                    if self.cleaned_data.get("walkin_from_date"):
                        walkin_from = self.cleaned_data["walkin_from_date"].strftime(
                            "%Y-%m-%d"
                        )
                        sqs = sqs.filter_and(
                            SQ(walkin_from_date__gte=walkin_from)
                            | SQ(walkin_to_date__gte=walkin_from)
                        )
                    if self.cleaned_data.get("walkin_to_date"):
                        walkin_to = self.cleaned_data["walkin_to_date"].strftime(
                            "%Y-%m-%d"
                        )
                        sqs = sqs.filter_and(
                            SQ(walkin_from_date__gte=walkin_to)
                            | SQ(walkin_to_date__lte=walkin_to)
                        )
            return sqs
        return []

    def query(self):
        """
        Return the query string if provided; otherwise, return None.
        """
        q_value = self.cleaned_data.get("q")
        return q_value if q_value else None
