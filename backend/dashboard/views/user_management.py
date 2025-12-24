import json

from django.contrib.auth.models import ContentType, Permission
from django.http.response import HttpResponse
from django.shortcuts import render

from mpcomp.views import permission_required
from peeldb.models import User, UserEmail

from ..forms import UserForm


# Functions to move here from main views.py:



@permission_required("activity_view", "activity_edit")
def admin_user_list(request):
    users_list = User.objects.filter(is_staff=True)

    return render(request, "dashboard/users/list.html", {"users_list": users_list})



@permission_required("")
def new_admin_user(request):
    if request.method == "POST":
        if User.objects.filter(email=request.POST["email"]).exists():
            user = User.objects.get(email=request.POST["email"])
            validate_user = UserForm(request.POST, request.FILES, instance=user)
        else:
            validate_user = UserForm(request.POST, request.FILES)
        if validate_user.is_valid():
            user, created = User.objects.get_or_create(
                email=request.POST["email"],
            )
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            if created:
                UserEmail.objects.create(
                    user=user, email=request.POST["email"], is_primary=True
                )
                user.username = request.POST["email"]
                user.first_name = request.POST["first_name"]
                user.last_name = request.POST["last_name"]
                user.address = request.POST["address"]
                user.permanent_address = request.POST["permanent_address"]

            if request.POST["mobile"]:
                user.mobile = request.POST["mobile"]
            if "gender" in request.POST and request.POST["gender"]:
                user.gender = request.POST["gender"]
            if "profile_pic" in request.FILES:
                user.profile_pic = request.FILES["profile_pic"]
            user.save()
            for perm in request.POST.getlist("user_type"):
                permission = Permission.objects.get(id=perm)
                user.user_permissions.add(permission)
                user.save()
            data = {"error": False, "response": "New user created"}
        else:
            data = {"error": True, "response": validate_user.errors}
        return HttpResponse(json.dumps(data))
    contenttype = ContentType.objects.get(model="user")
    permissions = (
        Permission.objects.filter(content_type_id=contenttype)
        .exclude(codename__icontains="jobposts")
        .exclude(codename__icontains="blog")
        .order_by("id")[3:]
    )
    return render(
        request, "dashboard/users/new_user.html", {"permissions": permissions}
    )



@permission_required("")
def view_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return render(request, "dashboard/404.html", status=404)
    return render(request, "dashboard/users/view.html", {"user": user})



@permission_required("")
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)
    if not user:
        return render(request, "dashboard/404.html", status=404)
    if request.method == "POST":
        validate_user = UserForm(request.POST, request.FILES, instance=user)
        if validate_user.is_valid():
            user = validate_user.save(commit=False)
            user.is_active = True
            user.is_superuser = True
            if "profile_pic" in request.FILES:
                user.profile_pic = request.FILES["profile_pic"]
            user.user_type = request.POST.get("user_type")
            user.last_name = request.POST.get("last_name")
            user.save()
            user.user_permissions.clear()
            for perm in request.POST.getlist("user_type"):
                permission = Permission.objects.get(id=perm)
                user.user_permissions.add(permission)
            data = {"error": False, "response": "Blog category created"}
        else:
            data = {"error": True, "response": validate_user.errors}
        return HttpResponse(json.dumps(data))
    contenttype = ContentType.objects.get(model="user")
    permissions = (
        Permission.objects.filter(content_type_id=contenttype)
        .exclude(codename__icontains="jobposts")
        .order_by("id")[3:]
    )
    return render(
        request,
        "dashboard/users/edit_user.html",
        {"permissions": permissions, "user": user},
    )


@permission_required("")
def delete_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        permissions = Permission.objects.filter(user=user)
        permission_list = [
            "activity_edit",
            "activity_view",
            "add_user",
            "change_user",
            "delete_user",
            "support_edit",
            "support_view",
        ]
        for permission in permissions:
            if permission.codename in permission_list:
                user.user_permissions.remove(permission)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        # user.delete()
        data = {"error": False, "response": "User Deleted"}
    else:
        data = {"error": True, "response": "Unable to delete user"}
    return HttpResponse(json.dumps(data))
