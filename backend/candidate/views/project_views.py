import datetime
import json
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from zoneinfo import ZoneInfo

from candidate.forms import ProjectForm
from peeldb.models import Project, Skill, City, User


@login_required
def add_project(request):
    if request.method == "GET":
        template = "candidate/add_project.html"
        return render(
            request,
            template,
            {
                "skills": Skill.objects.filter(status="Active"),
                "cities": City.objects.filter(status="Enabled"),
            },
        )
    project_form = ProjectForm(request.POST)
    if project_form.is_valid():
        if User.objects.filter(
            id=request.user.id, project__name=request.POST.get("name")
        ):
            data = {"error": True, "response_message": "Project already exists"}
            return HttpResponse(json.dumps(data))
        project = project_form.save()
        if request.POST.get("role"):
            project.role = request.POST.get("role")
        if request.POST.get("size"):
            project.size = request.POST.get("size")
        if request.POST.get("location"):
            project.location_id = request.POST.get("location")
        project.save()
        user = request.user
        user.profile_updated = timezone.now()
        user.save()
        user.project.add(project)
        data = {"error": False, "response": "project added"}
    else:
        data = {"error": True, "response": project_form.errors}
    return HttpResponse(json.dumps(data))


@login_required
def edit_project(request, project_id):
    projects = Project.objects.filter(id=project_id)
    if projects:
        if request.method == "GET":
            template = "candidate/edit_project.html"
            return render(
                request,
                template,
                {
                    "project": projects[0],
                    "skills": Skill.objects.filter(status="Active"),
                    "cities": City.objects.filter(status="Enabled"),
                },
            )
        project_form = ProjectForm(request.POST, instance=projects[0])
        if project_form.is_valid():
            if request.user.project.filter(name=request.POST.get("name")).exclude(
                id=project_id
            ):
                data = {"error": True, "response_message": "Project already exists"}
                return HttpResponse(json.dumps(data))
            project = project_form.save()
            if request.POST.get("role"):
                project.role = request.POST.get("role")
            if request.POST.get("size"):
                project.size = request.POST.get("size")
            if request.POST.get("location"):
                project.location_id = request.POST.get("location")
            project.save()
            user = request.user
            user.profile_updated = timezone.now()
            user.save()

            data = {"error": False, "response": "project added"}
        else:
            data = {"error": True, "response": project_form.errors}
        return HttpResponse(json.dumps(data))
    else:
        message = "Sorry, User with this Project not exists"
        template = "404.html"
        return render(request, template, {"message": message}, status=404)


@login_required
def delete_project(request, project_id):
    projects = Project.objects.filter(id=project_id)
    if projects:
        projects.delete()
        user = request.user
        user.profile_updated = timezone.now()
        user.save()
        data = {"error": False, "response": "Project deleted successfully"}
    else:
        data = {"error": True, "response": "Project not exist"}
    return HttpResponse(json.dumps(data))
