from django.contrib.gis import admin
from .models import Event, Image, Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_approved')
    list_filter = ('role', 'is_approved')
    search_fields = ('user__username',)


admin.site.register(Event)
admin.site.register(Image)
admin.site.register(Profile, ProfileAdmin)