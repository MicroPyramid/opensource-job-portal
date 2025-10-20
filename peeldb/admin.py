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
    simplecontact,
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


@admin.register(simplecontact)
class ContactInquiryAdmin(admin.ModelAdmin):
    """Admin interface for contact inquiries"""
    list_display = ('first_name', 'last_name', 'email', 'enquery_type', 'subject', 'contacted_on')
    list_filter = ('enquery_type', 'contacted_on')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'comment')
    readonly_fields = ('contacted_on',)
    date_hierarchy = 'contacted_on'
    ordering = ('-contacted_on',)

    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Inquiry Details', {
            'fields': ('enquery_type', 'subject', 'comment')
        }),
        ('Metadata', {
            'fields': ('contacted_on',)
        }),
    )
