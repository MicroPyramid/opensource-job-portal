import datetime
from datetime import date
import arrow
import re
from collections import Counter

from django import template
from django.conf import settings
from django.db.models import Count, Q, Prefetch
from django.core.cache import cache
from boto.s3.connection import S3Connection
from peeldb.models import (
    AppliedJobs,
    JobPost,
    User,
    City,
    Skill,
    State,
    Industry,
    Company,
    Qualification,
    AssessmentData,
    DEGREE_TYPES,
)
from mpcomp.views import str_to_list, mongoconnection
from candidate.forms import YEARS, MONTHS
from recruiter.forms import UserStatus
from pjob.calendar_events import get_calendar_events_list

register = template.Library()


@register.filter
def is_applied_for_job(user, job_post_id):
    if AppliedJobs.objects.filter(user_id=user, job_post_id=job_post_id):
        return True
    else:
        return False


@register.filter
def get_title(value):
    if len(value) > 54:
        if value[54] == "":
            return value[0:53]
        else:
            val = len(value[0:53].split(" ")[-1])
            val = 53 - val
            result = value[0:val]
            return result
    else:
        return value


@register.filter
def get_formatted_salary(value):
    import locale

    locale.setlocale(locale.LC_ALL, "en_IN.UTF-8")
    try:
        salary = locale.format("%d", int(value), grouping=True)
        return salary
    except:
        return value


@register.filter
def get_social_connections_count(user):
    connected = 0
    if user.twitter.all():
        connected += 1
    if user.linkedin.all():
        connected += 1
    if user.github.all():
        connected += 1
    if user.facebook.all():
        connected += 1
    if connected >= 2:
        return True
    else:
        return False


@register.filter
def get_string(value):
    return value.replace("_", " ")


@register.filter
def get_resume_name(value):
    resume_name = value.split("/")[-1]
    return resume_name


@register.filter
def get_s3_url(key):
    s3 = S3Connection(
        settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, is_secure=False
    )
    stored_url = s3.generate_url(
        600, "GET", bucket=settings.AWS_STORAGE_BUCKET_NAME, key=key, force_http=True
    )
    return stored_url


@register.filter
def check_perm(user):
    if user.has_perm("support_view") or user.has_perm("support_edit"):
        return True
    else:
        return False


@register.simple_tag
def get_latest_walkins():
    # import datetime
    # date = datetime.date.today()
    # start_week = date - datetime.timedelta(date.weekday())
    # end_week = start_week + datetime.timedelta(30)
    latest_walkins = cache.get("latest_walkins")
    if not latest_walkins:
        latest_walkins = (
            JobPost.objects.filter(job_type="walk-in", status="Live")
            .prefetch_related("location", "company")
            .order_by("-walkin_to_date")[:10]
        )
        cache.set("latest_walkins", latest_walkins, 60 * 60 * 48)

    # jobs_list = jobs_list.filter(Q(walkin_from_date__range=[start_week, end_week]) | Q(walkin_to_date__range=[start_week, end_week]))
    return latest_walkins


@register.simple_tag
def get_latest_jobposts():
    latest_jobposts = cache.get("latest_jobposts")
    if not latest_jobposts:
        latest_jobposts = JobPost.objects.filter(status="Live").exclude(
            job_type="walk-in"
        )[:10]
        cache.set("latest_jobposts", latest_jobposts, 60 * 5)
    return latest_jobposts


@register.simple_tag
def get_latest_recruiters():
    latest_recruiters = cache.get("latest_recruiters")
    if not latest_recruiters:
        latest_recruiters = (
            User.objects.filter(
                Q(user_type="RR")
                | Q(user_type="AR")
                | Q(user_type="AA") & Q(is_active=True)
            )
            .annotate(num_posts=Count("jobposts"))
            .prefetch_related("company")
            .order_by("-num_posts")[:7]
        )
        cache.set("latest_recruiters", latest_recruiters, 60 * 60 * 48)
    return latest_recruiters


@register.simple_tag(takes_context=True)
def get_page(context, page, no_pages):
    if page <= 3:
        start_page = 1
    else:
        start_page = page - 3

    if no_pages <= 6:
        end_page = no_pages
    else:
        end_page = start_page + 6

    if end_page > no_pages:
        end_page = no_pages

    pages = range(start_page, end_page + 1)
    return pages


@register.filter
def get_job_type(value):
    return value.job_type


@register.filter
def get_object_list_type(job_list, job_type):
    for job in job_list:
        if job.job_type == job_type:
            return True
    return False


@register.filter
def get_file_name(value):
    return value.name.split("/")[-1]


@register.filter
def get_name(value):
    return value.replace("\r\n", "").replace(",", "")


@register.filter
def get_industry_name(value):
    return str(value.split("/")[0].split("&")[0].strip())


@register.simple_tag
def get_industries():
    all_industries = cache.get("list_all_industries")
    if not all_industries:
        all_industries = (
            Industry.objects.filter(status="Active")
            .annotate(num_posts=Count("jobpost"))
            .order_by("-num_posts")[:17]
        )
        cache.set("list_all_industries", all_industries, 60 * 60 * 24)
    return all_industries


@register.simple_tag
def get_all_industries():
    all_industries = (
        Industry.objects.annotate(num_posts=Count("jobpost"))
        .filter(status="Active")
        .order_by("-num_posts")
    )
    return all_industries


@register.simple_tag
def get_skills():
    all_skills = cache.get("list_all_skills")
    if not all_skills:
        all_skills = (
            Skill.objects.annotate(num_posts=Count("jobpost"))
            .filter(status="Active")
            .exclude(name="Fresher")
            .order_by("-num_posts")
        )
        cache.set("list_all_skills", all_skills, 60 * 60 * 24)
    return all_skills[:17]


@register.simple_tag
def get_all_skills():
    all_skills = Skill.objects.annotate(num_posts=Count("jobpost"))
    all_skills = (
        all_skills.filter(status="Active")
        .exclude(name="Fresher")
        .order_by("-num_posts")
    )
    return all_skills


@register.simple_tag
def get_refine_skills(skills):
    all_refine_skills = cache.get("all_refine_skills")
    if not all_refine_skills:
        all_refine_skills = list(
            Skill.objects.filter(status="Active")
            .annotate(num_posts=Count("jobpost"))
            .order_by("-num_posts")
        )
        cache.set("all_refine_skills", all_refine_skills, 10000)
    if skills:
        each_skill = skills.annotate(num_posts=Count("jobpost")).order_by("num_posts")
        for each in each_skill.iterator():
            try:
                all_refine_skills.remove(each)
                all_refine_skills.insert(0, each)
            except:
                pass
    return all_refine_skills[:8]


@register.simple_tag
def get_refine_locations(locations):
    all_refine_locations = cache.get("all_refine_locations")
    if not all_refine_locations:
        all_refine_locations = list(
            City.objects.annotate(num_posts=Count("locations"))
            .filter(status="Enabled")
            .order_by("-num_posts")
        )
        cache.set("all_refine_locations", all_refine_locations, 10000)
    if locations:
        each_location = locations.annotate(num_posts=Count("locations")).order_by(
            "num_posts"
        )
        for each in each_location.iterator():
            try:
                all_refine_locations.remove(each)
                all_refine_locations.insert(0, each)
            except:
                pass
    return all_refine_locations[:8]


@register.simple_tag
def get_refine_states(states):
    all_refine_states = cache.get("all_refine_states")
    if not all_refine_states:
        all_refine_states = list(
            State.objects.annotate(num_posts=Count("state__locations"))
            .filter(status="Enabled")
            .order_by("-num_posts")
        )
        cache.set("all_refine_states", all_refine_states, 10000)
    if states:
        each_location = states.annotate(num_posts=Count("state__locations")).order_by(
            "num_posts"
        )
        for each in each_location.iterator():
            try:
                all_refine_states.remove(each)
                all_refine_states.insert(0, each)
            except:
                pass
    return all_refine_states[:8]


@register.simple_tag
def get_refine_industries(industry):
    all_refine_industries = cache.get("all_refine_industries")
    if not all_refine_industries:
        all_refine_industries = list(
            Industry.objects.annotate(num_posts=Count("jobpost"))
            .filter(status="Active")
            .order_by("-num_posts")
        )
        cache.set("all_refine_industries", all_refine_industries, 10000)
    if industry:
        each_industry = industry.annotate(num_posts=Count("jobpost")).order_by(
            "num_posts"
        )
        for each in each_industry.iterator():
            try:
                all_refine_industries.remove(each)
                all_refine_industries.insert(0, each)
            except:
                pass
    return all_refine_industries[:8]


@register.simple_tag
def get_refine_educations(education):
    all_refine_educations = cache.get("all_refine_educations")
    if not all_refine_educations:
        all_refine_educations = list(
            Qualification.objects.annotate(num_posts=Count("jobpost"))
            .filter(status="Active")
            .order_by("-num_posts")
        )
        cache.set("all_refine_educations", all_refine_educations, 10000)
    if education:
        each_edu = education.annotate(num_posts=Count("jobpost")).order_by("num_posts")
        for each in each_edu.iterator():
            try:
                all_refine_educations.remove(each)
                all_refine_educations.insert(0, each)
            except:
                pass
    return all_refine_educations[:8]


@register.simple_tag
def get_locations():
    all_locations = cache.get("list_all_locations")
    if not all_locations:
        all_locations = (
            City.objects.annotate(num_posts=Count("locations"))
            .filter(status="Enabled")
            .order_by("-num_posts")
        )
        cache.set("list_all_locations", all_locations, 60 * 60 * 48)
    return all_locations


@register.simple_tag
def get_full_time_jobs():
    all_jobs = cache.get("list_all_jobs")
    if not all_jobs:
        all_jobs = JobPost.objects.filter(job_type="full-time", status="Live").order_by(
            "-published_on"
        )[:10]
        cache.set("list_all_jobs", all_jobs, 60 * 60 * 48)
    return all_jobs


@register.simple_tag
def get_internships():
    internship_locations = cache.get("list_all_internship_jobs")
    if not internship_locations:
        internship_locations = (
            City.objects.filter(locations__job_type="internship", status="Enabled")
            .annotate(num_posts=Count("locations"))
            .distinct()
        )
        cache.set("list_all_internship_jobs", internship_locations, 60 * 60 * 24)
    return internship_locations[:17]


@register.simple_tag
def get_government_jobs():
    all_jobs = cache.get("list_all_government_jobs")
    if not all_jobs:
        all_jobs = JobPost.objects.filter(job_type="governament", status="Live")[:17]
        cache.set("list_all_government_jobs", all_jobs, 60 * 60 * 48)
    return all_jobs


@register.filter()
def change_to_int(value):
    return int(value)


@register.filter()
def filter_jobposts(value, status):
    return value.filter(status=status).count()


@register.filter()
def filter_users(value, status):
    return value.filter(is_active=status).count()


@register.simple_tag
def get_companies():
    all_companies = cache.get("list_all_companies")
    if not all_companies:
        all_companies = (
            Company.objects.filter(is_active=True)
            .annotate(num_posts=Count("jobpost"))
            .order_by("-num_posts")[:50]
        )
        cache.set("list_all_companies", all_companies, 60 * 60 * 48)
    return all_companies


@register.filter()
def get_skill_name(value):
    value = [x.replace(",", "") for x in value.split(", ") if x.strip()]
    return value


@register.filter()
def get_skill_count(value):
    value = [x.replace(",", "") for x in value.split(" ") if x.strip()]
    return len(value)


@register.filter
def is_connected(value):
    if User.objects.filter(email=value):
        return User
    return ""


@register.filter
def check_recruiter_perm(user, permission):
    if user.has_perm(permission):
        return True
    else:
        return False


@register.simple_tag
def get_current_date():
    today = arrow.utcnow().to("Asia/Calcutta").format("YYYY-MM-DD")
    current_date = datetime.datetime.strptime(today, "%Y-%m-%d").strftime("%d-%B-%Y")
    return current_date


@register.filter
def filter_mobile_users(value, status):
    return value.filter(mobile_verified=status).count()


@register.simple_tag
def get_recommended_jobposts(job):
    job = job.get_recommended_jobposts()
    return job[0:6], job[6:12], job[12:17]


@register.filter
def get_job_skills(job, skill):
    skills = list(job.skills.all())
    try:
        index = skills.index(skill)
    except:
        index = 0
    if index != 0:
        skills[0], skills[index] = skills[index], skills[0]
    return skills


@register.filter
def get_job_location(job, location):
    locations = list(job.location.all())
    try:
        index = locations.index(location)
    except:
        index = 0
    if index != 0:
        locations[0], locations[index] = locations[index], locations[0]
    return locations


@register.filter
def get_type(value):
    return str(value).lower()


@register.filter
def get_industry_type(value):
    return str(value.split("/")[0].lower())


@register.filter
def get_array(value):
    if type(value) == str:
        value = str_to_list(value)
    return value


@register.simple_tag
def get_user_status(user):
    form = UserStatus(user=user)
    return form


@register.filter
def is_job_applied(job, resume):
    if AppliedJobs.objects.filter(job_post=job, resume_applicant=resume):
        return True
    else:
        return False


@register.filter
def get_value_type(value):
    if type(value) == list:
        return True
    else:
        return False


@register.filter
def get_locations_list(value):
    if type(value) == str:
        value = value.replace("]", "")
        value = value.replace("[", "")
        value = value.replace("'", "")
        return value
    else:
        return value


@register.filter
def get_skills_list(value):
    if type(value) == str:
        value = str_to_list(value)
    return value


@register.filter
def get_skill_icon(value):
    skills = Skill.objects.filter(name__in=value)
    if skills and skills[0].icon and skills[0].status == "Active":
        return skills[0].icon
    else:
        return "http://cdn.peeljobs.com/jobopenings1.png"


@register.simple_tag
def get_qualifications():
    latest_qualifications = cache.get("latest_qualifications")
    if not latest_qualifications:
        latest_qualifications = (
            Qualification.objects.annotate(num_posts=Count("jobpost"))
            .filter(status="Active")
            .order_by("-num_posts")
        )
        cache.set("latest_qualifications", latest_qualifications, 60 * 60 * 48)
    return latest_qualifications


@register.simple_tag
def get_all_cities():
    latest_cities = cache.get("latest_cities")
    if not latest_cities:
        print("no cache")
        latest_cities = City.objects.filter(status="Enabled").order_by("name")
        cache.set("latest_cities", latest_cities, 60 * 60 * 48)
    return latest_cities


@register.simple_tag
def get_years():
    years = cache.get("years")
    if not years:
        years = YEARS
        cache.set("years", years, 60 * 60 * 48)
    return YEARS


@register.simple_tag
def get_months():
    months = cache.get("months")
    if not months:
        months = MONTHS
        cache.set("months", MONTHS, 60 * 60 * 48)
    return MONTHS


@register.simple_tag
def get_unread_messages(message_to, message_from, job_id):
    db = mongoconnection()
    messages = db.messages.count({"message_to": message_to.id, "is_read": False})
    if message_from:
        messages = db.messages.count(
            {
                "message_to": message_to.id,
                "is_read": False,
                "message_from": message_from.id,
                "job_id": None,
            }
        )
    if job_id:
        messages = db.messages.count(
            {
                "message_to": message_to.id,
                "is_read": False,
                "message_from": message_from.id,
                "job_id": job_id,
            }
        )
    return messages


@register.filter()
def get_obj_id(obj):
    return obj.get("_id")


@register.filter()
def is_resume_pdf(file):
    name_ext_list = file.split(".")
    if len(name_ext_list) > 1:
        ext = name_ext_list[int(len(name_ext_list) - 1)]
        if ext != "pdf":
            return False
    return True


@register.simple_tag
def get_related_skills(search_skills):
    status = search_skills[0].skill_type
    exclude = search_skills.values_list("id", flat=True)
    jobs = JobPost.objects.filter(skills__in=search_skills).prefetch_related(
        Prefetch(
            "skills",
            queryset=Skill.objects.filter(skill_type=status, status="Active").exclude(
                id__in=exclude
            ),
        )
    )
    skills = []
    for job in jobs:
        skills.extend(job.skills.all())
    if len(skills) < 20:
        latest = cache.get("get_top_skills")
        if not latest:
            latest = (
                Skill.objects.filter(status="Active")
                .exclude(id__in=exclude)
                .annotate(num_posts=Count("jobpost"))
                .order_by("-num_posts")
            )
            cache.set("get_top_skills", latest, 60 * 60 * 24)
        latest = latest.filter(skill_type=status)
        skills.extend(latest[:20])
    c = Counter(skills)
    final = c.most_common()
    return final[:20]


@register.filter()
def is_events_created(request, job):
    events = get_calendar_events_list(request)
    titles = [i["summary"] for i in events]
    if job.title in titles or not job.last_date or date.today() >= job.last_date:
        return True
    return False


@register.filter()
def is_liked_question(user, question):
    likes = AssessmentData.objects.filter(
        question__id=question, user=user, comment="", like=True
    )
    return likes.exists()


@register.filter()
def is_disliked_question(user, question):
    likes = AssessmentData.objects.filter(
        question__id=question, user=user, comment="", dislike=True
    )
    return likes.exists()


@register.filter()
def is_liked_answer(user, answer):
    likes = AssessmentData.objects.filter(
        solution__id=answer, user=user, comment="", like=True
    )
    return likes.exists()


@register.filter()
def is_disliked_answer(user, answer):
    likes = AssessmentData.objects.filter(
        solution__id=answer, user=user, comment="", dislike=True
    )
    return likes.exists()


@register.simple_tag()
def get_street_address(location, job):
    locations_count = job.location.all().count()
    job_locations = job.job_interview_location.all()
    for i in job_locations:
        if locations_count == 1 and job_locations.count() == 1:
            return i.venue_details, None
        elif location.name in i.venue_details:
            match = re.findall(r"\d{6}", i.venue_details)
            if match:
                return i.venue_details, match[0]
            return i.venue_details, None
    return None, None


@register.simple_tag
def get_all_qualifications():
    return Qualification.objects.filter(status="Active").order_by("name")


@register.simple_tag
def get_degree_type():
    return DEGREE_TYPES
