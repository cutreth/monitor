from django.contrib import admin
from monitor.models import Beer, Reading, Config

class ReadingInLine(admin.TabularInline):
    model = Reading
    extra = 1

class BeerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General Information',      {'fields': ['beer_text']}),
        ('Brew Notes',               {'fields': ['brew_date']}),
    ]
    inlines = [ReadingInLine]

class ReadingAdmin(admin.ModelAdmin):
    fieldsets = [
    ('Data',       {'fields': ['beer','temp_amb','temp_beer','temp_unit',
                               'light_amb']}),
    ('Instant',    {'fields': ['instant','instant_override']}),
    ('Errors',     {'fields': ['error_flag','error_details']}),
    ]

    readonly_fields = ('instant',)


admin.site.register(Beer, BeerAdmin)
admin.site.register(Config)
admin.site.register(Reading,ReadingAdmin)