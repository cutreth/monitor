from django.contrib import admin
from monitor.models import Beer, Reading, Config, Archive

class ReadingInLine(admin.TabularInline):
    model = Reading
    extra = 1
    
    fields = ('instant', 'instant_override','instant_actual','light_amb', 'pres_beer',
              'temp_amb', 'temp_beer', 'temp_unit', 'error_flag', 'error_details')
    readonly_fields = ('instant','instant_actual')

class BeerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General Information',      {'fields': ['beer_text']}),
        ('Brew Notes',               {'fields': ['brew_date']}),
    ]
    inlines = [ReadingInLine]

class ReadingAdmin(admin.ModelAdmin):
    fieldsets = [
    ('Instant',    {'fields': ['instant','instant_override','instant_actual']}),    
    ('Data',       {'fields': ['beer','light_amb','pres_beer','temp_amb',
                               'temp_beer','temp_unit']}),    
    ('Errors',     {'fields': ['error_flag','error_details']}),
    ]

    readonly_fields = ('instant','instant_actual')

admin.site.register(Beer, BeerAdmin)
admin.site.register(Config)
admin.site.register(Reading,ReadingAdmin)
admin.site.register(Archive)