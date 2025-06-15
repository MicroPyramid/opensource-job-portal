import json
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from peeldb.models import User, JobAlert, Subscriber


def applicant_unsubscribing(request, message_id):
    users = User.objects.filter(unsubscribe_code=message_id)
    if users:
        user = users[0]
        user.is_unsubscribe = True
        user.save()
    return HttpResponseRedirect("/")


def applicant_email_unsubscribing(request, email_type, message_id):
    if email_type == "alert":
        user = JobAlert.objects.filter(unsubscribe_code__iexact=message_id).first()
    elif email_type == "subscriber":
        user = Subscriber.objects.filter(unsubscribe_code__iexact=message_id).first()
    else:
        user = User.objects.filter(unsubscribe_code__iexact=message_id).first()
    if request.POST:
        if request.POST.get("reason") and user:
            user.is_unsubscribe = True
            user.unsubscribe_code = ""
            user.unsubscribe_reason = request.POST.get("reason")
            user.save()
            return HttpResponse(json.dumps({"error": False}))
        elif not user:
            return HttpResponse(
                json.dumps(
                    {"error": True, "err_message": "You are alredy Unsubscribed"}
                )
            )
        else:
            return HttpResponse(
                json.dumps({"error": True, "message": "* Please provide a reason!"})
            )
    if not user:
        return render(request, "unsubscribe_alerts.html", {"unsubscribed": True})
    return render(request, "unsubscribe_alerts.html")


@csrf_exempt
def bounces(request):
    body = request.body
    json_body = body.decode("utf8")
    js = json.loads(json_body.replace("\n", ""))
    if js["Type"] == "Notification":
        arg_info = js["Message"]
        arg_info = json.loads(arg_info.replace("\n", ""))
        if (
            "notificationType" in arg_info.keys()
            and arg_info["notificationType"] == "Bounce"
        ):
            bounce_email_address = arg_info["bounce"]["bouncedRecipients"]
            for each in bounce_email_address:
                user = User.objects.filter(email=each["emailAddress"])
                user.update(is_bounce=True)
                job_alerts = JobAlert.objects.filter(email=each["emailAddress"])
                job_alerts.delete()
                subscribers = Subscriber.objects.filter(email=each["emailAddress"])
                subscribers.delete()

    return HttpResponse("Bounced Email has been updated Sucessfully.")
