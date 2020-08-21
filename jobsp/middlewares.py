import re
from django.shortcuts import redirect
from mpcomp.views import mongoconnection
from django.core.cache import cache

try:
    import resource  # Not available on Win32 systems
except ImportError:
    resource = None
from django.utils.deprecation import MiddlewareMixin


# class StatsMiddleware(MiddlewareMixin):

#     def process_request(self, request):
#         temp = False
#         recruiters_list = ['/dashboard/recruiters/list/$',
#                            '^/dashboard/recruiter/view/(?P<user_id>[-\w]+)/$']
#         applicants_list = ['/dashboard/applicants/list/$',
#                            '^/dashboard/applicant/view/(?P<user_id>[a-zA-Z0-9_-]+)/$']
#         job_posts_list = ['/dashboard/jobpost/list/$',
#                           '^/dashboard/jobpost/view/(?P<job_id_id>[a-zA-Z0-9_-]+)/$']
#         data_list = ['/dashboard/country/$', '^/dashboard/functional_area/$', '^/dashboard/tech_skills/$',
#                      '^/dashboard/languages/$', '^/dashboard/qualifications/$', '^/dashboard/industries/$']
#         helpdesk = ['/dashboard/helpdesk/$']
#         dashboard = ['/dashboard/$']

#         recruiter_jobposts_list = ['/recruiter/job/list/$', '/recruiter/job/inactive/list/$',
#                                    '^/recruiter/job/view/(?P<job_post_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/job/edit/(?P<job_post_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/job/preview/(?P<job_post_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/job/applicants/(?P<job_post_id>[a-zA-Z0-9_-]+)/$']
#         recruiter_jobposts = ['/recruiter/job/new/$', '/recruiter/job/copy/$']
#         recruiter_profile = ['/recruiter/profile/$', '/recruiter/profile/edit/$',
#                              '/recruiter/mobile/verify/$',
#                              '/recruiter/send/mobile_verification_code/$']
#         recruiter_change_password = ['/recruiter/change_password/$']
#         recruiter_mailtemplates = ['^/recruiter/mail-template/list/(?P<jobpost_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/mail-template/new/(?P<jobpost_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/mail-template/edit/(?P<jobpost_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/mail-template/view/(?P<jobpost_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/mail-template/delete/(?P<jobpost_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/sent-mail/list/(?P<jobpost_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/sent-mail/view/(?P<sent_mail_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/sent-mail/delete/(?P<sent_mail_id>[a-zA-Z0-9_-]+)/$',
#                                    '^/recruiter/send_mail/(?P<jobpost_id>[a-zA-Z0-9_-]+)/(?P<template_id>[a-zA-Z0-9_-]+)/$']
#         recruiter_tickets = ['/tickets/$', '/tickets/ticket/new/$',
#                              '/tickets/ticket/list/$',
#                              '^/tickets/ticket/edit/(?P<ticket_id>[a-zA-Z0-9_-]+)/$',
#                              '^/tickets/ticket/view/(?P<ticket_id>[a-zA-Z0-9_-]+)/$']
#         jobs_list = ['/jobs/$', '/companies/$', '^/(?P<company_name>[-\w]+)-job-openings/$',
#                      '/recruiter/company/recruiters/$',
#                      '/recruiters/$', '^recruiters/(?P<recruiter_name>[a-zA-Z0-9_-]+.*?)/$']
#         jobs_applied = ['/jobs/applied/$']
#         jobs_by_location = ['/jobs-by-location/$']
#         jobs_by_industry = ['/jobs-by-industry/$']
#         jobs_by_skill = ['/jobs-by-skill/$']
#         job_alerts = ['/alert/create/$', '/alert/list/$', '/alert//$']
#         home_active = ['/page/terms-conditions/$', '/sitemap/$',
#                        '/page/faq/$', '/page/privacy-policy/$',
#                        '/page/terms-conditions/$', '/page/recruiter-faq/$']

#         if not temp:
#             for i in recruiters_list:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'recruiter'

#         if not temp:
#             for i in applicants_list:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'applicant'

#         if not temp:
#             for i in job_posts_list:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'job_post'

#         if not temp:
#             for i in data_list:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'data'

#         if not temp:
#             for i in helpdesk:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'helpdesk'

#         if not temp:
#             for i in dashboard:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'dashboard'

#         if not temp:
#             for i in recruiter_jobposts:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'recruiter_jobposts'

#         if not temp:
#             for i in recruiter_profile:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'recruiter_profile'

#         if not temp:
#             for i in recruiter_change_password:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'recruiter_change_password'

#         if not temp:
#             for i in recruiter_mailtemplates:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'recruiter_mailtemplates'

#         if not temp:
#             for i in recruiter_tickets:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'recruiter_tickets'

#         if not temp:
#             for i in recruiter_jobposts_list:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'recruiter_jobposts_list'

#         if not temp:
#             for i in jobs_list:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'jobs_list'

#         if not temp:
#             for i in jobs_applied:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'jobs_applied'

#         if not temp:
#             for i in jobs_by_location:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'jobs_by_location'

#         if not temp:
#             for i in jobs_by_skill:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'jobs_by_skill'

#         if not temp:
#             for i in jobs_by_industry:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'jobs_by_industry'

#         if not temp:
#             if re.match('/contact/$', request.path):
#                 temp = True
#                 request.session['url_id'] = 'contact_us'

#         if not temp:
#             if re.match('/my/user/password/change/$', request.path):
#                 temp = True
#                 request.session['url_id'] = 'change_password'

#         if not temp:
#             if re.match('/page/about-us/$', request.path):
#                 temp = True
#                 request.session['url_id'] = 'about_us'

#         if not temp:
#             for i in job_alerts:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'alerts'

#         if not temp:
#             if re.match('/profile/$', request.path):
#                 request.session['url_id'] = 'profile'

#         if not temp:
#             for i in home_active:
#                 if re.match(i, request.path):
#                     temp = True
#                     request.session['url_id'] = 'home'

#         # if not temp:
#         #     request.session['url_id'] = ''


reg_b = re.compile(
    r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino",
    re.I | re.M,
)
reg_v = re.compile(
    r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-",
    re.I | re.M,
)


class DetectMobileBrowser(MiddlewareMixin):
    def process_request(self, request):
        if "referer" not in request.session.keys():
            request.session["referer"] = request.META.get("HTTP_REFERER", "")
        if "is_mobile" not in request.session.keys():
            if request.META.get("HTTP_USER_AGENT", ""):
                user_agent = request.META["HTTP_USER_AGENT"]
                b = reg_b.search(user_agent)
                v = reg_v.search(user_agent[0:4])
                if b or v:
                    request.session["is_mobile"] = True
        request.is_mobile = request.session.get("is_mobile", False)


class LowerCased(MiddlewareMixin):
    def process_request(self, request):
        if not re.match("/social/user/update/$", request.path) and not re.match(
            "/logout/$", request.path
        ):
            if (
                request.user.is_authenticated
                and request.user.user_type == "JS"
                and request.user.registered_from == "Social"
                and not request.user.mobile
            ):
                return redirect("/social/user/update/", permanent=False)
        if request.path == "/recruiter/":
            return redirect("/post-job/", permanent=False)
        detail_page = re.match(
            "^/(?P<job_title_slug>[a-z0-9-.,*?]+)-(?P<job_id>([0-9])+)/$", request.path
        )
        blog_page = re.match("^/blog/(?P<blog_slug>[-\w]+)/$", request.path)
        if not detail_page and not blog_page:
            redirect_data = cache.get("redirect_data")
            if not redirect_data:
                db = mongoconnection()
                redirect_data = list(db.redirect_data.find())
                cache.set("redirect_data", redirect_data, 60 * 60 * 24)
            keys = [data["name"] for data in redirect_data]
            if any(match in request.path for match in keys):
                rep = {}
                for data in redirect_data:
                    rep[data["name"]] = data["slug"]
                url = request.path
                rep = dict((re.escape(k), v) for k, v in rep.items())
                pattern = re.compile("|".join(rep.keys()))
                url = pattern.sub(lambda m: rep[re.escape(m.group(0))], url)
                return redirect(url, permanent=True)
        if request.path == request.path.lower():
            return None
        return redirect(request.path.lower(), permanent=True)
