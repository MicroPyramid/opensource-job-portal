import datetime
import json
import random
from django.shortcuts import render
from django.http.response import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from zoneinfo import ZoneInfo

from mpcomp.s3_utils import S3Connection
from mpcomp.views import (
    jobseeker_login_required,
    get_resume_data,
    handle_uploaded_file,
)


@login_required
def upload_resume(request):
    """validate file size <250kb and type doc,docx,pdf,rtf,odt"""
    if "resume" in request.FILES and request.user.user_type == "JS":
        fo = request.FILES["resume"]
        sup_formates = [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/pdf",
            "application/rtf",
            "application/x-rtf",
            "text/richtext",
            "application/msword",
            "application/vnd.oasis.opendocument.text",
            "application/x-vnd.oasis.opendocument.text",
        ]
        ftype = fo.content_type
        size = fo.size / 1024
        if str(ftype) in sup_formates:
            if size < 300 and size > 0:
                conn = S3Connection(
                    settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY
                )
                random_string = "".join(
                    random.choice("0123456789ABCDEF") for i in range(3)
                )
                user_id = str(request.user.id) + str(random_string)
                path = (
                    "resume/"
                    + user_id
                    + "/"
                    + request.FILES["resume"]
                    .name.replace(" ", "-")
                    .encode("ascii", "ignore")
                    .decode("ascii")
                )
                conn.upload(
                    path,
                    request.FILES["resume"],
                    settings.AWS_STORAGE_BUCKET_NAME,
                    public=True,
                    expires="max",
                )
                request.user.resume = path
                request.user.profile_updated = timezone.now()
                handle_uploaded_file(
                    request.FILES["resume"], request.FILES["resume"].name
                )
                email, mobile, text = get_resume_data(request.FILES["resume"])
                request.user.resume_text = text
                if not request.user.mobile:
                    request.user.mobile = mobile
                request.user.save()
                data = {
                    "error": False,
                    "data": "Resume Uploaded Successfully",
                    "profile_percantage": request.user.profile_completion_percentage,
                    "upload_resume": True,
                    "email": email,
                    "resume_name": request.FILES["resume"].name,
                    "resume_path": "https://"
                    + settings.AWS_STORAGE_BUCKET_NAME
                    + ".s3.amazonaws.com/"
                    + path,
                }
            else:
                data = {"error": True, "data": "File Size must be less than 300 kb"}
        else:
            data = {
                "error": True,
                "data": "Please upload valid files For Ex: Doc, Docx, PDF, odt format",
            }
        return HttpResponse(json.dumps(data))
    elif request.user.user_type == "RR":
        data = {"error": True, "data": "Recruiter is not allowed to Subscribe"}
    elif request.user.is_staff:
        data = {"error": True, "data": "Admin is not allowed to Subscribe"}
    else:
        data = {
            "error": True,
            "data": "Upload your resume either in Doc or Docx or PDF or ODT format",
        }
    return HttpResponse(json.dumps(data))


@login_required
def upload_profilepic(request):
    """validate file size <250kb and type doc,docx,pdf,rtf,odt"""
    if "profile_pic" in request.FILES:
        pic = request.FILES["profile_pic"]
        sup_formates = ["image/jpeg", "image/png"]
        ftype = pic.content_type
        if str(ftype) in sup_formates:
            request.user.profile_pic = request.FILES["profile_pic"]
            request.user.profile_updated = timezone.now()
            request.user.save()
            data = {"error": False, "data": "Profile Pic Uploaded Successfully"}
        else:
            data = {
                "error": True,
                "data": "Please upload valid formats For Ex: JPEG, JPG, PNG format",
            }
    else:
        data = {
            "error": True,
            "data": "Upload your profile picture either in JPEG, JPG, PNG format",
        }
    return HttpResponse(json.dumps(data))


@login_required
def delete_resume(request):
    if request.method == "POST":
        request.user.resume = ""
        request.user.save()
        data = {"error": False, "response": "Your resume deleted Successfully"}
    else:
        data = {"error": False, "response": "Updated Successfully"}
    return HttpResponse(json.dumps(data))
