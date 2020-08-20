from django.conf import settings
import string
import random
import boto.ses
import urllib
import sendgrid
import requests
from math import floor
import arrow
import datetime
import operator

# from django.core.mail import EmailMultiAlternatives
from dateutil.relativedelta import relativedelta
from pytz import timezone
import re
from PIL import Image
import os
from .aws import AWS
import zipfile
from lxml import etree
from subprocess import Popen, PIPE

from django.contrib.auth.decorators import user_passes_test, login_required
from django.template import Template, Context, loader
from django.utils.crypto import get_random_string
from peeldb.models import Skill, City, Qualification, User, TechnicalSkill


def permission_required(*perms):
    return user_passes_test(
        lambda u: any(u.has_perm(perm) for perm in perms), login_url="/"
    )


def rand_string(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))


job_seeker_login_required = user_passes_test(
    lambda u: False if u.is_staff or u.is_recruiter else True, login_url="/"
)


def jobseeker_login_required(view_func):
    decorated_view_func = login_required(
        job_seeker_login_required(view_func), login_url="/"
    )
    return decorated_view_func


rec_login_required = user_passes_test(
    lambda u: True if u.is_recruiter or u.is_agency_recruiter else False, login_url="/"
)


def recruiter_login_required(view_func):
    decorated_view_func = login_required(
        rec_login_required(view_func), login_url="/recruiter/login/"
    )
    return decorated_view_func


age_login_required = user_passes_test(
    lambda u: True if u.is_agency_admin else False, login_url="/"
)


def agency_admin_login_required(view_func):
    decorated_view_func = login_required(
        age_login_required(view_func), login_url="/recruiter/login/"
    )
    return decorated_view_func


# mto is list like ['as@sd.xom', 'sf@ogf.com']
def Memail(mto, mfrom, msubject, mbody, user_active):
    from django.core.mail import send_mail, get_connection

    mfrom = settings.DEFAULT_FROM_EMAIL

    if user_active:
        send_mail(msubject, mbody, mfrom, mto, html_message=mbody, fail_silently=False)
    else:
        mailgun_backend = get_connection(
            "anymail.backends.mailgun.EmailBackend", api_key=settings.MAILGUN_API_KEY
        )
        send_mail(
            msubject,
            mbody,
            mfrom,
            mto,
            html_message=mbody,
            fail_silently=False,
            connection=mailgun_backend,
        )


def get_prev_after_pages_count(page, no_pages):
    prev_page = page - 1
    if prev_page == 1:
        previous_page = prev_page
    else:
        previous_page = prev_page - 1
    if page == 1:
        prev_page = page
        previous_page = page

    if page == no_pages:
        aft_page = no_pages
        after_page = no_pages
    else:
        aft_page = page + 1
        if aft_page == no_pages:
            after_page = no_pages
        else:
            after_page = aft_page + 1
    return prev_page, previous_page, aft_page, after_page


def mongoconnection():
    from pymongo import MongoClient

    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB]
    # db.authenticate(settings.MONGO_USER, settings.MONGO_PWD)
    return db


def opendocx(file):
    """Open a docx file, return a document XML tree"""
    mydoc = zipfile.ZipFile(file)
    xmlcontent = mydoc.read("word/document.xml")
    document = etree.fromstring(xmlcontent)
    return document


nsprefixes = {
    "mo": "http://schemas.microsoft.com/office/mac/office/2008/main",
    "o": "urn:schemas-microsoft-com:office:office",
    "ve": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    # Text Content
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w10": "urn:schemas-microsoft-com:office:word",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    # Drawing
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "mv": "urn:schemas-microsoft-com:mac:vml",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "v": "urn:schemas-microsoft-com:vml",
    "wp": ("http://schemas.openxmlformats.org/drawingml/2006/wordprocessing" "Drawing"),
    # Properties (core and extended)
    "cp": (
        "http://schemas.openxmlformats.org/package/2006/metadata/core-pr" "operties"
    ),
    "dc": "http://purl.org/dc/elements/1.1/",
    "ep": (
        "http://schemas.openxmlformats.org/officeDocument/2006/extended-" "properties"
    ),
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    # Content Types
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    # Package Relationships
    "r": ("http://schemas.openxmlformats.org/officeDocument/2006/relationsh" "ips"),
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    # Dublin Core document properties
    "dcmitype": "http://purl.org/dc/dcmitype/",
    "dcterms": "http://purl.org/dc/terms/",
}


def getdocumenttext(document):
    """Return the raw text of a document, as a list of paragraphs."""
    paratextlist = []
    # Compile a list of all paragraph (p) elements
    paralist = []
    for element in document.iter():
        # Find p (paragraph) elements
        if element.tag == "{" + nsprefixes["w"] + "}p":
            paralist.append(element)
    # Since a single sentence might be spread over multiple text elements,
    # iterate through each paragraph, appending all text (t) children to that
    # paragraphs text.
    for para in paralist:
        paratext = u""
        # Loop through each paragraph
        for element in para.iter():
            # Find t (text) elements
            if element.tag == "{" + nsprefixes["w"] + "}t":
                if element.text:
                    paratext = paratext + element.text
            elif element.tag == "{" + nsprefixes["w"] + "}tab":
                paratext = paratext + "\t"
        # Add our completed paragraph text to the list of paragraph text
        if paratext:
            paratextlist.append(paratext)
    return paratextlist


def document_to_text(filename, file_path):
    if filename[-4:] == ".doc":
        cmd = ["antiword", file_path]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode("ascii", "ignore")
    elif filename[-4:] == ".odt":
        cmd = ["odt2txt", file_path]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode("ascii", "ignore")


def remove_file(path):
    if os.path.exists(path):
        os.remove(path)


def handle_uploaded_file(file, filename):
    if not os.path.exists("resume/"):
        os.mkdir("resume/")

    with open("resume/" + filename, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def get_email_resume(text):
    email = mobile = ""
    if re.search(r"[0-9]{10}", text):
        mobile = re.search(r"[0-9]{10}", text).group(0)
    m = re.search(r"[\w\.-]+@[\w\.-]+", text)
    if m:
        email = m.group(0)
    return email, mobile


def get_resume_data(file):
    file_name = file.name
    file_format = file.name.split(".")[-1]
    f_name = file.name.split(".")[0]
    email = mobile = text = ""
    if file_format == "pdf":
        try:
            os.system(
                "pdftotext '%s' '%s'"
                % (
                    settings.BASE_DIR + "/resume/" + file_name,
                    settings.BASE_DIR + "/resume/" + f_name + ".txt",
                )
            )
            each = open(
                settings.BASE_DIR + "/resume/" + f_name + ".txt", "r"
            ).readlines()
            text = []
            for pdf_content in each:
                text.append(pdf_content)
                if re.search(r"[0-9]{10}", pdf_content):
                    mobile = re.search(r"[0-9]{10}", pdf_content).group(0)
                m = re.search(r"[\w\.-]+@[\w\.-]+", pdf_content)
                if m:
                    email = m.group(0)
            text = "\n\n".join(text)
        except:
            text = ""
    elif file_format == "doc":
        text = document_to_text(file_name, settings.BASE_DIR + "/resume/" + file_name)
        email, mobile = get_email_resume(text)
    elif file_format == "docx":
        document = opendocx(settings.BASE_DIR + "/resume/" + file_name)
        paratextlist = getdocumenttext(document)
        text = []
        for paratext in paratextlist:
            text.append(paratext)
        for paratext in paratextlist:
            if re.search(r"[0-9]{10}", (paratext)):
                mobile = re.search(r"[0-9]{10}", (paratext)).group(0)
            m = re.search(r"[\w\.-]+@[\w\.-]+", str(paratext.encode("utf-8")))
            if m:
                email = m.group(0)
        text = "\n\n".join(text)
    elif file_format == "odt":
        text = document_to_text(file_name, settings.BASE_DIR + "/resume/" + file_name)
        email, mobile = get_email_resume(text)
    remove_file(settings.BASE_DIR + "/resume/" + f_name + ".txt")
    remove_file(settings.BASE_DIR + "/resume/" + file_name)
    return email, mobile, text


def postonpeel_fb(job_post):
    params = {}
    params["message"] = job_post.published_message
    params["picture"] = settings.LOGO
    params["link"] = settings.PEEL_URL + str(job_post.get_absolute_url())

    job_name = (
        str(job_post.title)
        + ", for Exp "
        + str(job_post.min_year)
        + " - "
        + str(job_post.min_year)
    )

    # for index, location in enumerate(job_post.location.all()):
    #     job_name += str(location.name)
    #     if str(index) == str(location_count):
    #         job_name += str('.')
    #     else:
    #         job_name += str(', ')
    if job_post.company:
        params["description"] = job_post.company.name
    else:
        params["description"] = job_post.company_name

    params["access_token"] = settings.FB_PAGE_ACCESS_TOKEN
    params["name"] = job_name
    params["caption"] = "http://peeljobs.com"
    params["actions"] = [{"name": "get peeljobs", "link": "http://peeljobs.com/"}]

    params = urllib.parse.urlencode(params)
    # response = urllib.urlopen("https://graph.facebook.com/" + settings.FB_PEELJOBS_PAGEID + "/feed", params).read()
    u = requests.post("https://graph.facebook.com/190700467767653/feed", params=params)
    response = u.json()
    # response = json.loads(response)
    if "error" in response.keys():
        # found error, we need to log it for review.
        pass
    if "id" in response.keys():
        return "posted successfully"
    return "job not posted on page"


def float_round(num, places=0, direction=floor):
    num = float("%.10f" % num)
    no_of_digits = str(num)[::-1].find(".")
    if int(no_of_digits) <= 2:
        return num
    return direction(num * (10 ** places)) / float(10 ** places)


def get_current_date_time():
    today1 = arrow.utcnow().format("YYYY-MM-DD HH:MM:SS")
    today = datetime.datetime.strptime(str(today1), "%Y-%m-%d %H:%M:%S")
    published_date = datetime.datetime.strptime(
        str(today), "%Y-%m-%d %H:%M:%S"
    ) + datetime.timedelta(seconds=120)
    return published_date


def get_next_month():
    nextmonth = datetime.date.today() + relativedelta(months=1)
    nextmonth = datetime.datetime.strptime(str(nextmonth), "%Y-%m-%d").strftime(
        "%Y-%m-%d"
    )
    return nextmonth


def get_asia_time():
    asia_timezone = timezone(settings.TIMEZONE)
    asia_time = datetime.datetime.now(asia_timezone).strftime("%Y-%m-%d %H:%M:%S")
    published_date = datetime.datetime.strptime(
        str(asia_time), "%Y-%m-%d %H:%M:%S"
    ) - datetime.timedelta(seconds=3600)
    return published_date


def domain_check(value):
    return bool(re.match(r"^\A([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}\Z", value))


def custom_password_check(value):
    length_error = len(value) < 7
    digit_error = re.search(r"\d", value) is None
    string_error = re.search(r"[a-z,A-Z]", value) is None
    symbol_error = (
        re.search(r"[ !#$%&':;()?><*@+,-./[\\\]^_`{|}~" + r'"]', value) is None
    )
    password_ok = not (length_error or digit_error or string_error or symbol_error)
    if password_ok:
        return False
    return "Password must be a combination of characters, special characters and numbers with minimum length of 7"


def get_valid_skills_list(skill):
    final_skill = []
    s_list = Skill.objects.filter(slug__iexact=skill, status="Active")
    if s_list:
        final_skill.append(s_list[0].name)
    else:
        skill = skill.split("-")
        k = -1
        # final_skill = skill
        for i, j in enumerate(skill):
            # dupes = [j]
            if i <= k:
                continue
            while True:
                if j == "":
                    break
                sk = Skill.objects.filter(slug__iexact=j, status="Active")
                if sk.exists():
                    # skill = [l for l in skill if l not in j]
                    # final_skill = [x for x in final_skill if x not in dupes]
                    if sk[0].name not in final_skill:
                        final_skill.append(sk[0].name)
                i = i + 1
                if i < len(skill):
                    # dupes.append(skill[i])
                    j = j + "-" + skill[i]
                else:
                    break
    return final_skill


def get_valid_locations_list(location):
    final_location = []
    location = location.lower().split("-")
    k = -1
    if location != [""]:
        # final_location = location
        for i, j in enumerate(location):
            # dupes = [j]
            if i <= k:
                continue
            while True:
                if City.objects.filter(slug__iexact=j, status="Enabled"):
                    # location = [l for l in location if l not in j]
                    # final_location = [x for x in final_location if x not in dupes]
                    final_location.append(
                        City.objects.filter(slug__iexact=j, status="Enabled")[0].name
                    )
                    k = i
                    break
                i = i + 1
                if i < len(location):
                    # dupes.append(location[i])
                    j = j + "-" + location[i]
                else:
                    break
    return final_location


def get_valid_qualifications(skill):
    final_edu = []
    s_list = Qualification.objects.filter(slug__iexact=skill, status="Active")
    if s_list:
        final_edu.append(s_list[0].name)
    else:
        search_keywords = skill.split("-")
        skill = search_keywords
        for i, j in enumerate(skill):
            while True:
                if j == "":
                    break
                edu = Qualification.objects.filter(slug__iexact=j, status="Active")
                if edu.exists():
                    # skill = [l for l in skill if l not in j]
                    if edu[0].name not in final_edu:
                        final_edu.append(edu[0].name)
                i = i + 1
                if i < len(skill):
                    j = j + "-" + skill[i]
                else:
                    break
    return final_edu


def get_ordered_skill_degrees(text, skills, degrees):
    slugs = list(degrees.values_list("slug", flat=True)) + list(
        skills.values_list("slug", flat=True)
    )
    order = {}
    final = []
    for word in slugs:
        indexes = [w.start() for w in re.finditer(word, text)]
        order.update({word: indexes[0]})
    order_list = sorted(order.items(), key=operator.itemgetter(1))
    for search in order_list:
        skill = Skill.objects.filter(slug__iexact=search[0])
        if skill:
            final.append(skill[0].name)
        degree = Qualification.objects.filter(slug__iexact=search[0])
        if degree:
            final.append(degree[0].name)
    return final


def str_to_list(value):
    value = value.replace("[", "")
    value = value.replace("]", "")
    value = value.replace("'", "")
    value = value.replace(" ", "")
    value = value.replace('"', "")
    value = value.split(",")
    return value


def get_social_referer(request):
    social = {"fb": "facebook.com", "ln": "linkedin.com", "tw": "twitter.com"}
    if "HTTP_REFERER" in request.META.keys():
        refer = request.META["HTTP_REFERER"]
    else:
        refer = False
    for key, value in social.items():
        if refer:
            if refer.find(value) == -1:
                field = "otr"
            else:
                field = key
                break
        else:
            field = "otr"
    return field


def get_aws_file_path(input_file, folder_path, company_name):
    file_name = input_file.name.lower()
    file_name = re.sub("[^a-zA-Z0-9 \n\.]", "", file_name).replace(" ", "-")
    path = settings.BASE_DIR + "/static/"
    image_path = os.path.join(path, file_name)
    destination = open(image_path, "wb+")
    for chunk in input_file.chunks():
        destination.write(chunk)
    destination.close()
    # new_image = image_size(input_file, image_path)
    size = (200, 200)
    im = Image.open(image_path)
    im.thumbnail(size)
    # img_format = file_name.split('.')[-1]
    # if str(img_format) == 'jpg':
    #     img_format = 'JPEG'
    import magic

    im_format = magic.from_file(image_path, mime=True)
    if im_format == "image/jpeg":
        img_format = "JPEG"
    else:
        img_format = "png"
    im.convert("RGB").save(input_file, img_format)
    new_image = Image.new("RGB", size, color="#fff")
    new_image.convert("P")
    x_offset = (new_image.size[0] - im.size[0]) // 2
    y_offset = (new_image.size[1] - im.size[1]) // 2
    new_image.paste(im, (x_offset, y_offset))
    new_image.save(image_path, img_format)
    # from django.core.files.base import File

    # thumb_file = File(thumb_data)
    # ext = input_file.name.split(".")[-1]
    s3_url = AWS().push_to_s3(
        file_obj=open(os.path.join(path, file_name), "rb"),
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
        folder=folder_path,
        new_name=company_name + "." + img_format,
    )
    file_path = "https://" + settings.CLOUDFRONT_DOMAIN + "/" + s3_url[0]
    if os.path.exists(image_path):
        os.remove(image_path)
    return file_path


def get_absolute_url(job):
    qs = job.title.replace("/[^a-zA-Z-]/g", "").title().strip().strip(".")
    qs = qs.replace(" ", "-").lower()
    qs = qs.replace("/", "-").lower()
    qs = qs.replace(".", "dot-")
    if str(job.job_type) == "internship":
        if job.company:
            company_name = job.company.slug
        else:
            company_name = job.company_name
        qs = "/" + qs + "-" + str(company_name) + "-" + str(job.id) + "/"
    else:
        qs = (
            "/"
            + qs
            + "-"
            + str(job.min_year)
            + "-to-"
            + str(job.max_year)
            + "-years-"
            + str(job.id)
            + "/"
        )
    return qs


db = mongoconnection()


def get_404_meta(name, data):
    data["skill"] = ", ".join(data.get("skill")) if data.get("skill") else ""
    data["city"] = ", ".join(data.get("city")) if data.get("city") else ""
    meta_title = meta_description = ""
    meta = db.meta_data.find_one({"name": name})
    if meta:
        meta_title = Template(meta.get("meta_title")).render(Context(data))
        meta_description = Template(meta.get("meta_description")).render(Context(data))
    return meta_title, meta_description


def get_meta(name, data):
    page = data.get("page")
    meta_title = meta_description = h1_tag = ""
    meta = db.meta_data.find_one({"name": name})
    if meta:
        meta_title = Template(meta.get("meta_title")).render(
            Context({"current_page": page})
        )
        meta_description = Template(meta.get("meta_description")).render(
            Context({"current_page": page})
        )
        h1_tag = Template(meta.get("h1_tag")).render(Context({"current_page": page}))
    return meta_title, meta_description, h1_tag


def get_given_meta(value, data):
    meta_title = meta_description = h1_tag = ""
    if data.get("fresher"):
        if value.meta.get("fresher_meta_title"):
            meta_title = value.meta.get("fresher_meta_title")
        if value.meta.get("meta_description"):
            meta_description = value.meta.get("fresher_meta_description")
        if value.meta.get("fresher_h1_tag"):
            h1_tag = value.meta.get("fresher_h1_tag")
    elif data.get("walkin"):
        if value.meta.get("walkin_meta_title"):
            meta_title = value.meta.get("walkin_meta_title")
        if value.meta.get("walkin_meta_description"):
            meta_description = value.meta.get("walkin_meta_description")
        if value.meta.get("walkin_h1_tag"):
            h1_tag = value.meta.get("walkin_h1_tag")
    else:
        if value.meta.get("meta_title"):
            meta_title = value.meta.get("meta_title")
        if value.meta.get("meta_description"):
            meta_description = value.meta.get("meta_description")
        if value.meta.get("h1_tag"):
            h1_tag = value.meta.get("h1_tag")
    return meta_title, meta_description, h1_tag


def get_meta_data(name, data):
    locations = data.get("locations")
    skills = data.get("skills")
    page = data.get("page")
    final_location = (
        ", ".join(data.get("final_location")) if data.get("final_location") else ""
    )
    final_skill = ", ".join(data.get("final_skill")) if data.get("final_skill") else ""
    meta_title = meta_description = h1_tag = ""
    value = ""
    if not data.get("state") and locations and not skills and locations.count() == 1:
        value = locations[0]
    if skills and not locations and skills.count() == 1:
        value = skills[0]
    if value:
        meta_title, meta_description, h1_tag = get_given_meta(value, data)
    meta = db.meta_data.find_one({"name": name})
    if not meta_title and meta:
        meta_title = Template(meta.get("meta_title")).render(
            Context(
                {"city": final_location, "skill": final_skill, "current_page": page}
            )
        )
    if not meta_description and meta:
        meta_description = Template(meta.get("meta_description")).render(
            Context(
                {"city": final_location, "skill": final_skill, "current_page": page}
            )
        )
    if not h1_tag and meta:
        h1_tag = Template(meta.get("h1_tag")).render(
            Context(
                {"city": final_location, "skill": final_skill, "current_page": page}
            )
        )
    return meta_title, meta_description, h1_tag


def save_codes_and_send_mail(user, request, passwd):
    while True:
        random_code = get_random_string(length=15)
        if not User.objects.filter(activation_code__iexact=random_code):
            break
    while True:
        unsubscribe_code = get_random_string(length=15)
        if not User.objects.filter(unsubscribe_code__iexact=unsubscribe_code):
            break
    user.activation_code = random_code
    user.unsubscribe_code = unsubscribe_code
    user.save()
    skills = request.POST.getlist("technical_skills") or request.POST.getlist("skill")
    for s in skills:
        skill = Skill.objects.filter(id=s)
        if skill:
            tech_skill = TechnicalSkill.objects.create(skill=skill[0])
            user.skills.add(tech_skill)
    temp = loader.get_template("email/jobseeker_account.html")
    subject = "PeelJobs User Account Activation"
    url = (
        request.scheme
        + "://"
        + request.META["HTTP_HOST"]
        + "/user/activation/"
        + str(user.activation_code)
        + "/"
    )
    rendered = temp.render(
        {
            "activate_url": url,
            "user_email": user.email,
            "user_mobile": user.mobile,
            "user": user,
            "user_password": passwd,
            "user_profile": user.profile_completion_percentage,
        }
    )
    Memail(user.email, settings.DEFAULT_FROM_EMAIL, subject, rendered, False)


# def profile_completion(userid):
#     db=mongoconnection()
#     usr = db.PUser.find_one({'id':userid})
#     complete = 0
#     message = ''

#     sconnected =0
#     if 'gp_url' in usr.keys():
#         if usr['gp_url'] != '':

#             complete +=10
#             sconnected += 1
#         else:
#             message ="connect google account to increase chance of getting better job"
#     else:
#         message ="connect google account to increase chance of getting better job"

#     if 'fb_url' in usr.keys():
#         if usr['fb_url'] != '':
#             sconnected += 1

#     if 'tw_url' in usr.keys():
#         if usr['tw_url'] != '':
#             sconnected += 1

#     if 'ln' in usr.keys():
#         if usr['ln'] != '':
#             sconnected += 1

#     if 'git_url' in usr.keys():
#         if usr['git_url'] != '':
#             sconnected += 1

#     if 'sof_url' in usr.keys():
#         if usr['sof_url'] != '':
#             sconnected += 1


#     if 'res_key' in usr.keys():
#         if usr['res_key'] !='' :
#             complete += 10
#         else:
#             message = "Update resume to give recruiters better way of seeing your profile"

#     else:
#         message = "Update resume to give recruiters better way of seeing your profile"


#     # write for education and give 10
#     if 'ed_det' in usr.keys():
#         e=0
#         for i in usr['ed_det']:
#             e+=1
#         print e
#         if e > 0:
#             complete +=10
#         else:
#             message = "add education details to increase chance of getting better job"
#     else:
#         message = "add education details to increase chance of getting better job"

#     # write for skills and give 10
#     if 'skill' in usr.keys():
#         s=0
#         for i in usr['skill']:
#             s+=1
#         if s > 1:
#             complete +=10
#         else:
#             message = "add atleast two skills to increase chance of getting better job"
#     else:
#         message = "add atleast two skills to increase chance of getting better job"


#     # write for languages and give 10
#     if 'lang' in usr.keys():
#         l=0
#         for i in usr['lang']:
#             l+=1
#         if l > 0:
#             complete +=10
#         else:
#             message = "add language info to increase chance of getting better job"
#     else:
#         message = "add language info to increase chance of getting better job"


#     # write for Projects and give 10
#     if 'wrk_his' in usr.keys():

#         wp=0
#         for wrk in usr['wrk_his']:
#             if 'proj' in wrk:
#                 for i in wrk['proj']:
#                     wp+=1

#         if wp > 0:
#             print "ok"
#             complete +=10

#         else:

#             message ="add projects to increase chance of getting better job"


#     else:
#         print "second"
#         message ="add projects to increase chance of getting better job"


#     # write personal info and give 10
#     if 'fname' in usr.keys() and 'lname' in usr.keys() and 'cur_loc' in usr.keys() and 'pre_loc' in usr.keys():
#         complete +=10
#     else:
#         message ="add personal details to increase chance of getting better job"

#     # write for professional info and give 10
#     if 'rloc' in usr.keys() and 'role' in usr.keys():
#         complete +=10
#     else:
#         message ="add relocation and role to increase chance of getting better job"

#     # profile header 5
#     if 'header' in usr.keys():
#         complete +=5
#     else:
#         message ="add profile description to increase chance of getting better job"

#     # total experience 5
#     if 'tot_exp' in usr.keys():
#         complete +=5
#     else:
#         message ="add total experience to increase chance of getting better job"

#     if sconnected >= 2:

#         complete += 10

#     else:
#         message = "connect to 2 or more social networks to increase chance of getting better job"


#     #db.PUser.update profile completion percentage
#     db.PUser.update({'id':userid},{'$set':{'prof_per':complete}})


#     data = {'complete':complete, 'message':message}
#     return data

# # v = MCValidate()
# # v.validate(request, Key, ValueType, **{'Required':'', 'ErrorText':'', 'MinLen':'', 'MaxLen':'', 'RegEx':''})

# class MCValidate():

#     def __init__(self):
#         self.err = {}

#     def validate(self, request, Key, ValueType, Required=True, ErrorText='', MinLen=0, MaxLen=0, RegEx=''):
#     #def validate(self, request, **kwargs):

#         # check according to MaxLen value if its not 0.


#         # check according to MinLen value if its not 0.
#         if MaxLen > 0:
#                 if len(request.get(Key)) > MaxLen:
#                     if ErrorText == "":
#                         self.err[Key]= 'Too long to process'
#                     else:
#                         self.err[Key]= ErrorText
#                     return

#         if MinLen > 0:
#             if len(request.get(Key)) < MinLen:
#                     if ErrorText == "":
#                         self.err[Key]= 'Too short to process'
#                     else:
#                         self.err[Key]= ErrorText
#                     return

#         if ValueType == "Email":
#             # https://pypi.python.org/pypi/validate_email/1.0
#             from validate_email import validate_email

#             if not validate_email(request.get(Key)):
#                 if ErrorText == "":
#                     self.err[Key]= 'Invalid Email Address'
#                 else:
#                     self.err[Key]= ErrorText

#                 return

#         elif ValueType == "Number":
#             try:

#                 int(request.get(Key))

#                 return
#             except:
#                 if ErrorText == "":
#                     self.err[Key]= 'Not a integer value'
#                 else:
#                     self.err[Key]= ErrorText
#                 return

#         elif ValueType == "Decimal":
#             try:
#                 float(request.get(Key))
#                 return

#             except:
#                 if ErrorText == "":
#                     self.err[Key]= 'Not a Decimal value'
#                 else:
#                     self.err[Key]= ErrorText
#                 return


#         elif ValueType == "String":
#             try:
#                 str(request.get(Key))
#                 return
#             except:
#                 if ErrorText == "":
#                     self.err[Key]= 'Not a string value'
#                 else:
#                     self.err[Key]= ErrorText
#                 return


#         elif ValueType == "RegEx":
#             import re
#             if RegEx != "":
#                 regexp=re.compile(r'%s'% re.escape(RegEx))
#                 if regexp.search(request.get(Key)) is None:
#                     if ErrorText == "":
#                         self.err[Key]= 'Not in given format'
#                     else:
#                         self.err[Key]= ErrorText
#             return


#         elif ValueType == "Url":

#             from django.core.validators import URLValidator


#             validate = URLValidator()
#             try:
#                 validate(request.get(Key))
#             except:
#                 if ErrorText == "":
#                         self.err[Key]= 'enter valid url'
#                 else:
#                         self.err[Key]= ErrorText
#                 return


#         elif ValueType == "Date":

#             try:
#                 time.strptime(request.get(Key), '%m/%d/%Y')
#                 return
#             except:
#                 if ErrorText == "":
#                         self.err[Key]= 'not in mm/dd/yyyy format'
#                 else:
#                         self.err[Key]= ErrorText
#                 return


#         elif ValueType == "DateTime":

#             try:
#                 time.strptime(request.get(Key), '%m/%d/%Y:%H:%M:%S')
#                 return
#             except:
#                 if ErrorText == "":
#                         self.err[Key]= 'not in correct format'
#                 else:
#                         self.err[Key]= ErrorText
#                 return


#     def eval(self):
#         return self.err


#
