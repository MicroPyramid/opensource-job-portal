import datetime
import json
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.db.models import Q, Case, When
from django.template.loader import render_to_string

from mpcomp.views import jobseeker_login_required
from peeldb.models import User, JobPost, UserMessage


def get_messages(request):
    if request.POST.get("job_id"):
        UserMessage.objects.filter(
            message_to=request.user.id, job=int(request.POST.get("job_id"))
        ).update(is_read=True)

        messages = UserMessage.objects.filter(
            job__id=int(request.POST.get("job_id"))
            & (Q(message_from=request.user.id) | Q(message_to=request.user.id))
        )

    else:
        UserMessage.objects.filter(
            message_to=request.user.id, message_from=int(request.POST.get("r_id"))
        ).update(is_read=True)

        messages = UserMessage.objects.filter(
            Q(
                message_from=request.user.id,
                message_to=int(request.POST.get("r_id")),
                job__id=None,
            )
            | Q(
                message_from=int(request.POST.get("r_id")),
                message_to=request.user.id,
                job__id=None,
            )
        )

    user = User.objects.filter(id=request.POST.get("r_id")).first()
    job = JobPost.objects.filter(id=request.POST.get("job_id")).first()
    try:
        user_pic = user.profile_pic.url
    except:
        user_pic = user.photo
    try:
        profile_pic = request.user.profile_pic.url
    except:
        profile_pic = request.user.photo
    if not user_pic:
        user_pic = "https://cdn.peeljobs.com/dummy.jpg"
    if not profile_pic:
        profile_pic = "https://cdn.peeljobs.com/dummy.jpg"
    if user:
        messages = render_to_string(
            "candidate/messages.html",
            {
                "messages": messages,
                "user": user,
                "job": job,
                "user_pic": user_pic,
                "profile_pic": profile_pic,
            },
            request,
        )
        data = {"error": False, "messages": messages}
    else:
        data = {"error": True, "response": "User Not Found!"}
    return data


@jobseeker_login_required
def messages(request):
    """need to check user login or not"""
    if request.POST.get("mode") == "get_messages":
        data = get_messages(request)
        return HttpResponse(json.dumps(data))
    if request.POST.get("post_message"):

        msg = UserMessage.objects.create(
            message=request.POST.get("message"),
            message_from=request.user,
            message_to=User.objects.get(id=int(request.POST.get("message_to"))),
        )

        if request.POST.get("job_id"):
            msg.job = int(request.POST.get("job_id"))

        time = datetime.datetime.now().strftime("%b. %d, %Y, %l:%M %p")
        return HttpResponse(
            json.dumps(
                {
                    "error": False,
                    "message": request.POST.get("message"),
                    "job_post": request.POST.get("job_id"),
                    "msg_id": str(msg.id),
                    "time": time,
                }
            )
        )
    if request.POST.get("mode") == "delete_message":
        msg = UserMessage.objects.get(id=request.POST.get("id"))
        if msg.message_from == request.user or msg.message_to == request.user:
            msg.delete()
            data = {"error": False, "message": request.POST.get("message")}
        else:
            data = {"error": True, "message": "You cannot delete!"}
        return HttpResponse(json.dumps(data))
    if request.POST.get("mode") == "delete_chat":
        if request.POST.get("job"):
            UserMessage.objects.filter(
                message_from=request.user.id,
                message_to=int(request.POST.get("user")),
                job=int(request.POST.get("job")),
            ).delete()
            UserMessage.objects.filter(
                message_from=int(request.POST.get("user"), message_to=request.user.id),
                job=int(request.POST.get("job")),
            ).delete()

        else:
            UserMessage.objects.filter(
                message_from=request.user.id,
                message_to=int(request.POST.get("user")),
                job=None,
            ).delete()
            UserMessage.objects.filter(
                message_from=int(request.POST.get("user")),
                message_to=request.user.id,
                job=None,
            ).delete()

        return HttpResponse(
            json.dumps({"error": False, "message": request.POST.get("message")})
        )
    if request.user.is_authenticated:
        messages = UserMessage.objects.filter(message_to=request.user.id)

        job_ids = messages.values_list("job__id", flat=True).distinct()
        recruiter_ids = messages.values_list("message_from__id", flat=True).distinct()
        jobs = JobPost.objects.filter(id__in=job_ids)
        users = User.objects.filter(id__in=recruiter_ids)
        if jobs.exists():
            job_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(job_ids)])
            jobs = jobs.order_by(job_order)
        if users.exists():
            recruiter_order = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(recruiter_ids)]
            )
            users = users.order_by(recruiter_order)
        template = "candidate/user_messages.html"
        return render(request, template, {"recruiters": users, "jobs": jobs})
    else:
        return HttpResponseRedirect("/")
