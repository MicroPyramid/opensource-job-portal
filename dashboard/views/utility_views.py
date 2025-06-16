import json
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.cache import cache

from mpcomp.views import permission_required
from peeldb.models import (
    AgencyCompanyBranch,
    AgencyResume,
    City,
    Degree,
    EducationInstitue,
    JobAlert,
    JobPost,
    MetaData,
    Project,
    Qualification,
    Question,
    SearchResult,
    Skill,
    Subscriber,
    TechnicalSkill,
    User,
)

from ..forms import MetaForm


# Functions to move here from main views.py:

@login_required
def aws_push_to_s3(request):
    if request.method == "POST":
        if request.FILES.get("upload_file"):
            blog_post = Post.objects.filter(id=request.POST.get("post_id"))
            if blog_post:
                attachment = BlogAttachment.objects.create(
                    post=blog_post[0],
                    uploaded_by=request.user,
                    attached_file=request.FILES.get("upload_file"),
                )
                return HttpResponse(
                    json.dumps(
                        {
                            "error": False,
                            "response": "Please Upload An Image",
                            "url": str(settings.STATIC_URL)
                            + str(attachment.attached_file.name),
                            "name": attachment.attached_file.name,
                            "id": attachment.id,
                        }
                    )
                )
            return HttpResponse(
                json.dumps(
                    {
                        "error": True,
                        "response": "Blog post is not exist, please try again",
                    }
                )
            )
        return HttpResponse(
            json.dumps({"error": True, "response": "Please Upload An Image"})
        )


@login_required
def aws_del_from_s3(request):
    if request.method == "POST":
        if request.POST.get("attachment_id"):
            blog_attachment = BlogAttachment.objects.filter(
                id=request.POST.get("attachment_id")
            )
            if blog_attachment:
                blog_attachment.delete()
                return HttpResponse(
                    json.dumps(
                        {"error": False, "response": "Attachment Deleted Successfully"}
                    )
                )
            return HttpResponse(
                json.dumps(
                    {
                        "error": True,
                        "response": "Blog post is not exist, please try again",
                    }
                )
            )
    return HttpResponse(
        json.dumps({"error": True, "response": "Please Upload An Image"})
    )



def updating_meta_data():
    skills = Skill.objects.filter(status="Active", slug="java")
    for skill in skills:

        meta_title = (
            skill.meta["meta_title"] if "meta_title" in skill.meta.keys() else ""
        )
        meta_description = (
            skill.meta["meta_description"]
            if "meta_description" in skill.meta.keys()
            else ""
        )
        walkin_meta_title = meta_title.replace(" Jobs", " Walkins").replace(
            "Openings", "Vacancies"
        )
        walkin_meta_description = (
            meta_description.replace("jobs", "Walkins")
            .replace("openings", "Vacancies")
            .replace("Jobs", "Walkins")
            .replace("Openings", "Vacancies")
        )
        meta = skill.meta
        meta["walkin_meta_title"] = walkin_meta_title
        meta["walkin_meta_description"] = walkin_meta_description
        skill.meta = meta
        skill.save()




@permission_required("activity_edit")
def save_meta_data(request):
    if request.POST:
        if request.POST.get("mode") == "add_data":
            mform = MetaForm(request.POST)
            if mform.is_valid():
                mform.save()
                return HttpResponse(
                    json.dumps({"error": False, "response": "Data Added Successfuly"})
                )
            return HttpResponse(json.dumps({"error": True, "response": mform.errors}))
        if request.POST.get("mode") == "edit_data":
            instance = get_object_or_404(MetaData, id=request.POST.get("meta_id"))
            form = MetaForm(request.POST or None, instance=instance)
            if form.is_valid():
                form.save()

                return HttpResponse(
                    json.dumps({"error": False, "response": "Updated Successfully"})
                )
            return HttpResponse(json.dumps({"error": True, "response": form.errors}))
        if request.POST.get("mode") == "delete_data":
            if MetaData.objects.get(pk=request.POST.get("meta_id")):
                MetaData.objects.get(pk=request.POST.get("meta_id")).delete()
            return HttpResponse(
                json.dumps({"error": False, "response": "Removed Successfully!"})
            )
    meta_data = MetaData.objects.all()
    return render(
        request, "dashboard/base_data/save_meta_data.html", {"meta_data": meta_data}
    )


@permission_required("activity_edit")
def moving_duplicates(request, value):
    if value == "skills":
        values = Skill.objects.annotate(num_posts=Count("jobpost"))
        if request.method == "POST":
            if request.POST.getlist("duplicates"):
                duplicates = Skill.objects.filter(
                    id__in=request.POST.getlist("duplicates")
                )
                original = Skill.objects.filter(id=request.POST.get("original")).first()
                search_results = SearchResult.objects.filter(skills__in=duplicates)
                for search in search_results:
                    for skill in duplicates:
                        search.skills.remove(skill)
                    search.skills.add(original)
                alerts = JobAlert.objects.filter(skill__in=duplicates)
                for alert in alerts:
                    for skill in duplicates:
                        alert.skill.remove(skill)
                    alert.skill.add(original)
                major_skill_jobs = JobPost.objects.filter(major_skill__in=duplicates)
                major_skill_jobs.update(major_skill=original)
                tech_skills = TechnicalSkill.objects.filter(skill__in=duplicates)
                tech_skills.update(skill=original)
                jobposts = JobPost.objects.filter(skills__in=duplicates)
                for job in jobposts:
                    for skill in duplicates:
                        job.skills.remove(skill)
                    job.skills.add(original)
                users = User.objects.filter(technical_skills__in=duplicates)
                for user in users:
                    for skill in duplicates:
                        user.technical_skills.remove(skill)
                    user.technical_skills.add(original)
                projects = Project.objects.filter(skills__in=duplicates)
                for project in projects:
                    for skill in duplicates:
                        project.skills.remove(skill)
                    project.skills.add(original)
                agency_resumes = AgencyResume.objects.filter(skill__in=duplicates)
                for resume in agency_resumes:
                    for skill in duplicates:
                        resume.skill.remove(skill)
                    resume.skill.add(original)
                subscribers = Subscriber.objects.filter(skill__in=duplicates)
                subscribers.update(skill=original)
                questions = Question.objects.filter(skills__in=duplicates)
                questions.update(skills=original)
                return HttpResponse(
                    json.dumps(
                        {"error": False, "response": "Skills updated successfully"}
                    )
                )
            return HttpResponse(
                json.dumps(
                    {"error": True, "response": "Please Select the duplicate Skills"}
                )
            )
    elif value == "degrees":
        values = Qualification.objects.annotate(num_posts=Count("jobpost"))
        if request.method == "POST":
            if request.POST.getlist("duplicates"):
                original = Qualification.objects.filter(
                    id=request.POST.get("original")
                ).first()
                duplicates = Qualification.objects.filter(
                    id__in=request.POST.getlist("duplicates")
                )
                jobs = JobPost.objects.filter(edu_qualification__in=duplicates)
                for job in jobs:
                    for deg in duplicates:
                        job.edu_qualification.remove(deg)
                    job.edu_qualification.add(original)
                degrees = Degree.objects.filter(degree_name__in=duplicates)
                degrees.update(degree_name=original)
                return HttpResponse(
                    json.dumps(
                        {"error": False, "response": "Degrees updated successfully"}
                    )
                )
            return HttpResponse(
                json.dumps(
                    {"error": True, "response": "Please Select the duplicate Degrees"}
                )
            )
    elif value == "locations":
        values = City.objects.annotate(num_posts=Count("locations")).annotate(
            user_count=Count("current_city")
        )
        if request.method == "POST":
            if request.POST.getlist("duplicates"):
                duplicates = City.objects.filter(
                    id__in=request.POST.getlist("duplicates")
                )
                original = City.objects.filter(id=request.POST.get("original")).first()
                users = User.objects.filter(city__in=duplicates)
                users.update(city=original)
                current_users = User.objects.filter(current_city__in=duplicates)
                current_users.update(current_city=original)
                preferred_users = User.objects.filter(preferred_city__in=duplicates)
                for user in preferred_users:
                    for city in duplicates:
                        user.preferred_city.remove(city)
                    user.preferred_city.add(original)
                jobs = JobPost.objects.filter(location__in=duplicates)
                for job in jobs:
                    for city in duplicates:
                        job.location.remove(city)
                    job.location.add(original)
                alerts = JobAlert.objects.filter(location__in=duplicates)
                for alert in alerts:
                    for city in duplicates:
                        alert.location.remove(city)
                    alert.location.add(original)
                searches = SearchResult.objects.filter(locations__in=duplicates)
                for search in searches:
                    for city in duplicates:
                        search.locations.remove(city)
                    search.locations.add(original)
                institutes = EducationInstitue.objects.filter(city__in=duplicates)
                institutes.update(city=original)
                Projects = Project.objects.filter(location__in=duplicates)
                Projects.update(location=original)
                agency_branches = AgencyCompanyBranch.objects.filter(
                    location__in=duplicates
                )
                agency_branches.update(location=original)
                return HttpResponse(
                    json.dumps(
                        {"error": False, "response": "Locations updated successfully"}
                    )
                )
            return HttpResponse(
                json.dumps(
                    {"error": True, "response": "Please Select the duplicate Locations"}
                )
            )
    return render(
        request, "dashboard/duplicates.html", {"values": values, "status": value}
    )


@permission_required("activity_edit")
def clear_cache(request):
    cache.clear()
    return HttpResponseRedirect("/dashboard/")
