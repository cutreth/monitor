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

admin.site.register(Beer, BeerAdmin)
admin.site.register(Config)