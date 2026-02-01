from django.contrib import admin
from django.db.models import Count
from peeldb.models import (
    User,
    Google,
    Country,
    State,
    City,
    Skill,
    Industry,
    UserEmail,
    Language,
    Qualification,
    FunctionalArea,
    simplecontact,
)


class LocationAdminMixin:
    """
    Mixin for location models (Country, State, City) to restrict permissions.
    Added as part of location cleanup initiative (LOCATION_CLEANUP_PLAN.md Phase 1)

    Only superusers can add/edit/delete locations to maintain data quality.
    """

    def has_add_permission(self, request):
        """Only superusers can create locations"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Only superusers can edit locations"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete locations"""
        return request.user.is_superuser


@admin.register(Country)
class CountryAdmin(LocationAdminMixin, admin.ModelAdmin):
    """Admin interface for Country model"""
    list_display = ('id', 'name', 'slug', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'slug')
    ordering = ('name',)


@admin.register(State)
class StateAdmin(LocationAdminMixin, admin.ModelAdmin):
    """Admin interface for State model"""
    list_display = ('id', 'name', 'country', 'slug', 'status')
    list_filter = ('country', 'status')
    search_fields = ('name', 'slug')
    ordering = ('country__name', 'name')
    raw_id_fields = ('country',)


@admin.register(City)
class CityAdmin(LocationAdminMixin, admin.ModelAdmin):
    """Admin interface for City model"""
    list_display = ('id', 'name', 'state', 'get_country', 'status', 'job_count')
    list_filter = ('status', 'state__country', 'state')
    search_fields = ('name', 'slug')
    ordering = ('state__name', 'name')
    raw_id_fields = ('state',)
    readonly_fields = ('job_count',)

    def get_country(self, obj):
        """Display country name"""
        return obj.state.country.name if obj.state and obj.state.country else '-'
    get_country.short_description = 'Country'
    get_country.admin_order_field = 'state__country__name'

    def job_count(self, obj):
        """Display number of jobs using this city"""
        from peeldb.models import JobPost
        count = JobPost.objects.filter(location=obj).count()
        return count
    job_count.short_description = 'Jobs'

    def get_queryset(self, request):
        """Optimize queryset with prefetch"""
        qs = super().get_queryset(request)
        return qs.select_related('state', 'state__country')


admin.site.register(Skill)
admin.site.register(Language)
admin.site.register(FunctionalArea)
admin.site.register(Industry)
admin.site.register(User)
admin.site.register(Google)
admin.site.register(UserEmail)
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
