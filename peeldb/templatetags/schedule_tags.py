from django import template
import calendar
from django.template import loader, Context
from django.utils.dates import WEEKDAYS, WEEKDAYS_ABBR
from django.template.loader import render_to_string

weekday_names = []
weekday_abbrs = []


# The calendar week starts on Sunday, not Monday
weekday_names.append(WEEKDAYS[6])
weekday_abbrs.append(WEEKDAYS_ABBR[6])
for i in range(6):
    weekday_names.append(WEEKDAYS[i])
    weekday_abbrs.append(WEEKDAYS_ABBR[i])

register = template.Library()


@register.simple_tag(takes_context=True)
def month_table(context, request, month, size="regular"):
    each = {}
    each["day_names"] = weekday_abbrs
    each["month"] = month
    each["pp_action_points"] = []
    each["year"] = context["year"]
    each["jobs_list"] = context["jobs_list"]
    each["calendar_events"] = context["calendar_events"]
    # each['week'] = each['week']
    if size == "regular":
        template_name = "calendar/partials/_month_table.html"
    else:
        template_name = "calendar/partials/_month_table_large.html"
    message = render_to_string(template_name, each)

    return message


@register.filter(name="get_weekdays")
def get_weekdays(year, month):
    cobj = calendar.Calendar(calendar.SUNDAY)
    return cobj.monthdayscalendar(year, month)


@register.simple_tag(takes_context=True)
def week_table(context):
    cobj = calendar.Calendar(calendar.SUNDAY)
    try:
        week_days = cobj.monthdayscalendar(
            int(context["year"]), int(context["month"]["id"])
        )[int(context["week"]) - 1]
    except IndexError:
        week_days = cobj.monthdayscalendar(
            int(context["year"]), int(context["month"]["id"])
        )[0]
    context["week_days"] = week_days
    template_name = "calendar/partials/_day_cells.html"
    t = loader.get_template(template_name)
    return t.render(Context(context))


@register.filter
def get_client_first_letter(name):
    client_name = ""
    if name.split(" "):
        list = name.split(" ")
        for n in list:
            client_name += n[0]
        return client_name
    else:
        if name:
            return name[0]
        else:
            return "None"


@register.simple_tag(takes_context=True)
def get_per_day_jobposts(context, year, month, date):
    import datetime

    if context["jobs_list"]:
        day = datetime.date(int(year), int(month), int(date))
        if context["jobs_list"]:
            jobs_list = context["jobs_list"].filter(last_date=day)
        else:
            jobs_list = []
        return jobs_list
    return ""


@register.simple_tag(takes_context=True)
def get_per_day_events(context, year, month, date):
    import datetime

    if context["calendar_events"]:
        day = datetime.date(int(year), int(month), int(date))
        date_events = []
        for i in context["calendar_events"]:
            if str(day) >= str(i["start_date"]) and str(day) <= str(i["end_date"]):
                date_events.append(i)
        return date_events
    return ""
