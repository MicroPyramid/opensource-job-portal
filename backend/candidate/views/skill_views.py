import datetime
import json
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from zoneinfo import ZoneInfo

from candidate.forms import (
    TechnicalSkillForm,
    YEARS,
    MONTHS,
)
from peeldb.models import (
    Language,
    UserLanguage,
    Skill,
    TechnicalSkill,
    TechnicalSkill_STATUS,
)


@login_required
def add_language(request):
    if request.method == "GET":
        languages = Language.objects.all()
        template = "candidate/add_language.html"
        return render(request, template, {"languages": languages})
    if request.POST.get("language"):
        if request.user.language.filter(language_id=request.POST.get("language")):
            data = {
                "error": True,
                "response_message": "You have already created this langugae in your profile",
            }
            return HttpResponse(json.dumps(data))
        read = request.POST.get("read") == "on"
        write = request.POST.get("write") == "on"
        speak = request.POST.get("speak") == "on"
        if read or write or speak:
            language = Language.objects.get(id=request.POST.get("language"))
            language = UserLanguage.objects.create(
                language=language, read=read, write=write, speak=speak
            )
            user = request.user
            request.user.language.add(language)
            user.profile_updated = timezone.now()
            request.user.save()
            data = {"error": False, "response": "language added"}
        else:
            data = {
                "error": True,
                "language": "Please Select atleast any read/write/speak  option",
            }
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": "Please select the language"}
        return HttpResponse(json.dumps(data))


@login_required
def edit_language(request, language_id):
    user_language = UserLanguage.objects.filter(user=request.user, id=language_id)
    if request.method == "GET":
        languages = Language.objects.all()
        if user_language:
            template = "candidate/editlanguage.html"
            data = {"language": user_language[0], "languages": languages}
        else:
            template = "404.html"
            data = {
                "message": "Sorry, User with this language not exists",
                "reason": "The URL may be misspelled or the language you're looking for is no longer available.",
            }
        return render(request, template, data, status=200 if user_language else 404)
    if request.POST.get("get_lang"):
        lan = UserLanguage.objects.filter(user=request.user, id=language_id).first()
        data = {
            "error": False,
            "id": lan.language.id,
            "read": lan.read,
            "write": lan.write,
            "speak": lan.speak,
        }
        return HttpResponse(json.dumps(data))
    if request.POST.get("edit_lang") and request.POST.get("language"):
        read = request.POST.get("read") == "on"
        write = request.POST.get("write") == "on"
        speak = request.POST.get("speak") == "on"
        if read or write or speak:
            language = user_language[0]
            lang = Language.objects.get(id=request.POST.get("language"))
            language.language = lang
            language.read = read
            language.write = write
            language.speak = speak
            language.save()
            user = request.user
            user.profile_updated = timezone.now()
            user.save()
            data = {"error": False, "response": "language updated"}
        else:
            data = {
                "error": True,
                "response": "Please Select atleast any read/write/speak option",
            }
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": "Please select the language"}
        return HttpResponse(json.dumps(data))


@login_required
def delete_language(request, language_id):
    user_language = UserLanguage.objects.filter(user=request.user, id=language_id)
    if user_language:
        language = user_language[0]
        language.delete()
        user = request.user
        user.profile_updated = timezone.now()
        user.save()

        data = {"error": False, "message": "language deleted successfully"}
    else:
        data = {"error": True, "errinfo": "language not exist"}
    return HttpResponse(json.dumps(data))


@login_required
def add_technicalskill(request):
    if request.method == "GET":
        user_skills = request.user.skills.values_list("skill", flat=True)
        skills = (
            Skill.objects.filter(status="Active")
            .exclude(id__in=user_skills)
            .order_by("name")
        )
        template = "candidate/add_technicalskill.html"
        return render(
            request,
            template,
            {
                "years": YEARS,
                "months": MONTHS,
                "skills": skills,
                "status": TechnicalSkill_STATUS,
            },
        )
    technical_skill = TechnicalSkillForm(request.POST, requested_user=request.user)
    if technical_skill.is_valid():
        if request.user.skills.filter(skill__id=request.POST.get("skill")):
            data = {
                "error": True,
                "response_message": "You have already created this skill in your profile",
            }
            return HttpResponse(json.dumps(data))
        skill = technical_skill.save()
        if request.POST.get("last_used"):
            last_used = datetime.datetime.strptime(
                request.POST.get("last_used"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            skill.last_used = last_used
        skill.version = request.POST.get("version")
        skill.proficiency = request.POST.get("proficiency")
        user = request.user
        user.profile_updated = timezone.now()
        skill.is_major = True if request.POST.get("is_major") else False
        skill.save()
        user.save()
        user.skills.add(skill)
        data = {
            "error": False,
            "response": "techskills added",
            "profile_percantage": request.user.profile_completion_percentage,
            "technical_skill": True,
        }
    else:
        data = {"error": True, "response": technical_skill.errors}
    return HttpResponse(json.dumps(data))


@login_required
def edit_technicalskill(request, technical_skill_id):
    skill = TechnicalSkill.objects.filter(id=technical_skill_id)
    if skill:
        if request.method == "GET":
            skills = Skill.objects.filter(status="Active").order_by("name")
            template = "candidate/edit_technicalskill.html"
            return render(
                request,
                template,
                {
                    "years": YEARS,
                    "months": MONTHS,
                    "skills": skills,
                    "technical_skill": skill[0],
                    "status": TechnicalSkill_STATUS,
                },
            )
        technical_skill = TechnicalSkillForm(
            request.POST, requested_user=request.user, instance=skill[0]
        )
        if technical_skill.is_valid():
            if request.user.skills.filter(skill_id=request.POST.get("skill")).exclude(
                id=technical_skill_id
            ):
                data = {
                    "error": True,
                    "response_message": "You have already created this skill in your profile",
                }
                return HttpResponse(json.dumps(data))
            technical_skill = technical_skill.save(commit=False)
            if request.POST.get("last_used"):
                last_used = datetime.datetime.strptime(
                    request.POST.get("last_used"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                technical_skill.last_used = last_used
            technical_skill.version = request.POST.get("version")
            technical_skill.proficiency = request.POST.get("proficiency")
            user = request.user
            user.profile_updated = timezone.now()
            user.save()
            technical_skill.is_major = True if request.POST.get("is_major") else False
            technical_skill.save()
            data = {"error": False, "response": "skillinfo updated successfully"}
        else:
            data = {"error": True, "response": technical_skill.errors}
        return HttpResponse(json.dumps(data))
    else:
        message = "Sorry, User with this Technical Skill not exists"
        template = "404.html"
        return render(request, template, {"message": message}, status=404)


@login_required
def delete_technicalskill(request, technical_skill_id):
    skill = TechnicalSkill.objects.filter(id=technical_skill_id)
    if skill:
        skill.delete()
        user = request.user
        user.profile_updated = timezone.now()
        user.save()
        data = {"error": False, "response": "tech skill deleted successfully"}
    else:
        data = {"error": True, "response": "tech skill not exist"}
    return HttpResponse(json.dumps(data))
