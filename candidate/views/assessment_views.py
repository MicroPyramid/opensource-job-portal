import json
import math
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import Template, Context

from mpcomp.views import get_prev_after_pages_count
from peeldb.models import (
    MetaData,
    Question,
    JobPost,
    AssessmentData,
    Solution,
)


def question_view(request, que_id):
    question = Question.objects.filter(status="Live", id=que_id).first()
    latest_questions = Question.objects.filter(status="Live").order_by("-modified_on")
    meta_title = meta_description = h1_tag = ""
    if question:
        meta = MetaData.objects.filter(name="question_view")
        if meta:
            meta_title = Template(meta[0].meta_title).render(Context({}))
            meta_description = Template(meta[0].meta_description).render(Context({}))
            h1_tag = Template(meta[0].h1_tag).render(Context({}))
        return render(
            request,
            "assessments/question_view.html",
            {
                "question": question,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
                "latest_questions": latest_questions[:7],
            },
        )
    template = "404.html"
    data = {
        "message": "Sorry, Question does not exists",
        "reason": "The URL may be misspelled or the language you're looking for is no longer available.",
    }
    return render(request, template, data, status=404)


def assessments_questions(request, **kwargs):
    current_url = reverse("assessments_questions")
    questions = Question.objects.filter(status="Live")
    latest_jobs = (
        JobPost.objects.filter(status="Live")
        .exclude(job_type="walk-in")
        .select_related("company")
        .prefetch_related("location", "skills")[:7]
    )
    search = request.GET.get("search", "")
    if search:
        questions = questions.filter(title__icontains=search)
    items_per_page = 20
    no_of_que = questions.count()
    no_pages = int(math.ceil(float(no_of_que) / items_per_page))
    page = kwargs.get("page_num", 1)
    if page and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("assessments_questions"))
        else:
            page = int(page)
    else:
        page = 1
    questions = questions[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    meta_title = meta_description = h1_tag = ""
    meta = MetaData.objects.filter(name="question_view")
    if meta:
        meta_title = Template(meta[0].meta_title).render(Context({}))
        meta_description = Template(meta[0].meta_description).render(Context({}))
        h1_tag = Template(meta[0].h1_tag).render(Context({}))
    return render(
        request,
        "assessments/questions_list.html",
        {
            "questions": questions,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "current_url": current_url,
            "no_of_que": no_of_que,
            "latest_jobs": latest_jobs,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
            "search": search,
        },
    )


def assessment_changes(request):
    user = request.user
    if request.POST.get("mode") == "add_like":
        model = request.POST.get("model")
        obj_id = request.POST.get("id")
        if model == "question":
            like = AssessmentData.objects.filter(
                question=Question.objects.get(id=int(obj_id)), user=user, comment=""
            ).first()
            if like:
                like.like = True
                like.dislike = False
                like.save()
            else:
                AssessmentData.objects.create(
                    question=Question.objects.get(id=int(obj_id)), user=user, like=True
                )
        else:
            like = AssessmentData.objects.filter(
                solution=Solution.objects.get(id=int(obj_id)), user=user, comment=""
            ).first()
            if like:
                like.like = True
                like.dislike = False
                like.save()
            else:
                AssessmentData.objects.create(
                    solution=Solution.objects.get(id=int(obj_id)), like=True, user=user
                )
        return HttpResponse(json.dumps({"error": False}))
    if request.POST.get("mode") == "dis_like":
        model = request.POST.get("model")
        obj_id = request.POST.get("id")
        if model == "question":
            dislike = AssessmentData.objects.filter(
                question=Question.objects.get(id=int(obj_id)), user=user, comment=""
            ).first()
            if dislike:
                dislike.like = False
                dislike.dislike = True
                dislike.save()
            else:
                AssessmentData.objects.create(
                    question=Question.objects.get(id=int(obj_id)),
                    user=user,
                    dislike=True,
                )
        else:
            dislike = AssessmentData.objects.filter(
                solution=Solution.objects.get(id=int(obj_id)), user=user, comment=""
            ).first()
            if dislike:
                dislike.like = False
                dislike.dislike = True
                dislike.save()
            else:
                AssessmentData.objects.create(
                    solution=Solution.objects.get(id=int(obj_id)),
                    dislike=True,
                    user=user,
                )
        return HttpResponse(json.dumps({"error": False}))
    if request.POST.get("mode") == "add_comment":
        if request.POST.get("comment"):
            model = request.POST.get("model")
            obj_id = request.POST.get("id")
            if model == "question":
                AssessmentData.objects.create(
                    question=Question.objects.get(id=int(obj_id)),
                    user=user,
                    comment=request.POST.get("comment"),
                )
            else:
                AssessmentData.objects.create(
                    solution=Solution.objects.get(id=int(obj_id)),
                    user=user,
                    comment=request.POST.get("comment"),
                )
            return HttpResponse(
                json.dumps({"error": False, "comment": request.POST.get("comment")})
            )
        else:
            return HttpResponse(
                json.dumps({"error": True, "message": "Please enter your comment"})
            )
    return HttpResponse(json.dumps({"error": True}))
