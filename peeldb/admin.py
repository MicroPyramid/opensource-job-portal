from django.contrib import admin
from peeldb.models import (
    User,
    Google,
    Facebook,
    Country,
    State,
    City,
    Skill,
    Industry,
    UserEmail,
    GitHub,
    Language,
    Qualification,
    FunctionalArea,
)

admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Skill)
admin.site.register(Language)
admin.site.register(FunctionalArea)
admin.site.register(Industry)
admin.site.register(User)
admin.site.register(Google)
admin.site.register(Facebook)
admin.site.register(UserEmail)
admin.site.register(GitHub)
admin.site.register(Qualification)
