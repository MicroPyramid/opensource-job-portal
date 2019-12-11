from django.conf.urls import url
from pjob.views import (index, job_apply, user_applied_job,
                        jobs_applied, job_add_event,
                        get_skills)

app_name = "pjob"

urlpatterns = [

    url(r'^$', index, name="index"),
    # url(r'(?P<jp>((\w{0,})-(?P<jid>(\w{0,})))+)(?:\/(?P<uid>[A-Za-z0-9]+))?/$','job_detail'),
    url(r'apply/(?P<job_id>[a-zA-Z0-9_-]+)/$', job_apply, name="job_apply"),
    url(r'applied_for/$', user_applied_job, name="user_applied_job"),
    url(r'applied/$', jobs_applied, name="jobs_applied"),
    url(r'add/event/$', job_add_event, name="job_add_event"),
    url(r'get_skills/$', get_skills, name="get_skills"),
    url(r'^(?P<page_num>[0-9]+)/$', index),
]
