from django.contrib import admin
from portal_misc.models import BankHoliday

@admin.register(BankHoliday)
class BankHolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'is_active', 'added_by', 'added_on')
    list_filter = ('is_active',)
    search_fields = ('description',)
