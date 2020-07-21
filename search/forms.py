from haystack.forms import SearchForm
from django import forms
from haystack.query import SearchQuerySet
from haystack.query import SQ
from peeldb.models import City

valid_time_formats = ["%Y-%m-%d 00:00:00"]


class job_searchForm(SearchForm):
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

        # sqs = SearchQuerySet().models(JobPost).filter(status='Live')
        sqs = SearchQuerySet()
        sqs = sqs.filter_and(status="Live")
        if not self.is_valid():
            return sqs
        if self.cleaned_data["q"] and self.cleaned_data["location"]:
            term = self.cleaned_data["q"]
            term = term.replace("[", "")
            term = term.replace("]", "")
            term = term.replace("'", "")
            # sqs = sqs.filter_and(SQ(title=term) | SQ(designation=term)| SQ(skills=term))
            terms = [t.strip() for t in term.split(",")]
            sqs = sqs.filter_and(
                SQ(title__in=terms) | SQ(designation__in=terms) | SQ(skills__in=terms)
            )
            # sqs = sqs.filter_or(SQ(designation__in=terms))
            # sqs = sqs.filter_or(SQ(skills__in=terms))
            location = self.cleaned_data["location"]
            location = location.replace("[", "")
            location = location.replace("]", "")
            location = location.replace("'", "")
            locations = [t.strip() for t in location.split(",")]
            other_cities = City.objects.filter(name__in=locations).values_list(
                "parent_city__name", flat=True
            )
            sqs = sqs.filter_and(
                SQ(location__in=locations)
                | SQ(location__startswith=self.cleaned_data["location"])
                | SQ(location__in=other_cities)
            )

            if self.cleaned_data["job_type"]:
                sqs = sqs.filter_and(job_type=self.cleaned_data["job_type"])

            if self.cleaned_data["industry"]:
                term = self.cleaned_data["industry"]
                # sqs = sqs.filter_and(SQ(title=term) | SQ(designation=term)| SQ(skills=term))
                terms = [t.strip() for t in term.split(",")]
                sqs = sqs.filter_or(industry__in=terms)

            if self.cleaned_data["functional_area"]:
                term = self.cleaned_data["functional_area"]
                # sqs = sqs.filter_and(SQ(title=term) | SQ(designation=term)| SQ(skills=term))
                terms = [t.strip() for t in term.split(",")]
                sqs = sqs.filter_or(functional_area__in=terms)

            if self.cleaned_data["experience"] or self.cleaned_data["experience"] == 0:
                sqs = sqs.filter_or(
                    SQ(max_experience__gte=self.cleaned_data["experience"])
                    & SQ(min_experience__lte=self.cleaned_data["experience"])
                )

            if self.cleaned_data["salary"]:
                sqs = sqs.filter_or(
                    SQ(max_salary__gte=self.cleaned_data["salary"])
                    & SQ(min_salary__lte=self.cleaned_data["salary"])
                )
            if self.cleaned_data["walkin_type"]:
                import datetime

                if self.cleaned_data["walkin_type"] == "this_week":
                    date = datetime.date.today()
                    start_week = (
                        date
                        - datetime.timedelta(date.weekday())
                        - datetime.timedelta(1)
                    )
                    end_week = start_week + datetime.timedelta(6)
                    start_week = datetime.datetime.strptime(
                        str(start_week), "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")
                    end_week = datetime.datetime.strptime(
                        str(end_week), "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")
                    sqs = sqs.filter_and(
                        SQ(walkin_from_date__range=[start_week, end_week])
                        | SQ(walkin_to_date__range=[start_week, end_week])
                    )
                if self.cleaned_data["walkin_type"] == "next_week":
                    date = datetime.date.today()
                    start_week = (
                        date
                        - datetime.timedelta(date.isoweekday())
                        + datetime.timedelta(7)
                    )
                    end_week = start_week + datetime.timedelta(6)
                    start_week = datetime.datetime.strptime(
                        str(start_week), "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")
                    end_week = datetime.datetime.strptime(
                        str(end_week), "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")
                    sqs = sqs.filter_and(
                        SQ(walkin_from_date__range=[start_week, end_week])
                        | SQ(walkin_to_date__range=[start_week, end_week])
                    )

                    # sqs = sqs.filter_and(SQ(walkin_from_date__range=[start_week, end_week]) | SQ(walkin_to_date__range=[start_week, end_week]))
                if self.cleaned_data["walkin_type"] == "this_month":
                    current_date = datetime.date.today()
                    from dateutil.relativedelta import relativedelta
                    from datetime import date

                    start_week = date(current_date.year, current_date.month, 1)
                    end_week = start_week + relativedelta(day=31)
                    start_week = datetime.datetime.strptime(
                        str(start_week), "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")
                    end_week = datetime.datetime.strptime(
                        str(end_week), "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")
                    sqs = sqs.filter_and(
                        SQ(walkin_from_date__range=[start_week, end_week])
                        | SQ(walkin_to_date__range=[start_week, end_week])
                    )
                # if self.cleaned_data['walkin_type'] == 'next_month':
                #     pass
                if self.cleaned_data["walkin_type"] == "custom_range":
                    if self.cleaned_data["walkin_from_date"]:
                        walkin_from_date = datetime.datetime.strptime(
                            str(self.cleaned_data["walkin_from_date"]), "%Y-%m-%d"
                        ).strftime("%Y-%m-%d")
                        sqs = sqs.filter_and(
                            SQ(walkin_from_date__gte=walkin_from_date)
                            | SQ(walkin_to_date__gte=walkin_from_date)
                        )
                    if self.cleaned_data["walkin_to_date"]:
                        walkin_to_date = datetime.datetime.strptime(
                            str(self.cleaned_data["walkin_to_date"]), "%Y-%m-%d"
                        ).strftime("%Y-%m-%d")
                        sqs = sqs.filter_and(
                            SQ(walkin_from_date__gte=walkin_to_date)
                            | SQ(walkin_to_date__lte=walkin_to_date)
                        )
            return sqs
        else:
            return []

    def query(self):
        if self.cleaned_data["q"]:
            return self.cleaned_data["q"]
        return None


# 13-11-2014
# 20-11-2014 29-11-2014
