from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Client, Contract, Bank, Currency, Bank_account, Request, Request_type, Approval, Ordering, Payment_type, Additional_file, Role,UserProfile, Email_templates, History, Initiator, RequestExecutor, Individual_bank_account, Individual, Mission, Mission_type, Country_of_residence
from django_celery_beat import admin as celery_admin
from pwa_webpush.models import PushInformation

class MyAdminSite(admin.AdminSite):
    site_header = 'CC administration'
    site_title = 'CC admin'

admin_site = MyAdminSite(name='CC')

class RequestExecutorInline(GenericTabularInline):
    model = RequestExecutor
    extra = 1

class InitiatorInline(GenericTabularInline):
    model = Initiator
    extra = 1

class OrderingInline(GenericTabularInline):
    model = Ordering
    extra = 1

class Individual_bank_accountInline(admin.TabularInline):
    model = Individual_bank_account
    extra = 0

class Bank_accountInline(admin.TabularInline):
    model = Bank_account
    extra = 0

class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0

class Additional_fileInline(GenericTabularInline):
    model = Additional_file
    extra = 0

class Mission_typeAdmin(admin.ModelAdmin):
    inlines = [InitiatorInline, OrderingInline, RequestExecutorInline]
    search_fields = ['name']

class Request_typeAdmin(admin.ModelAdmin):
    inlines = [InitiatorInline, OrderingInline, RequestExecutorInline]
    search_fields = ['name']

class IndividualAdmin(admin.ModelAdmin):
    inlines = [Individual_bank_accountInline]
    list_display = ('name',)
    search_fields = ('name',)

class ClientAdmin(admin.ModelAdmin):
    inlines = [ContractInline,Bank_accountInline]
    list_display = ('name','biin')
    search_fields = ['name','biin']

class MissionAdmin(admin.ModelAdmin):
    inlines = [Additional_fileInline]
    list_display = ('client','individual')
    search_fields = ('client.name','individual.name')

class RequestAdmin(admin.ModelAdmin):
    inlines = [Additional_fileInline]
    list_display = ('client','sum')
    search_fields = ('client.name','sum')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False

class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username','first_name','last_name')
    search_fields = ('username','first_name','last_name')
   


# unregister old user admin
#admin_site.unregister(User)
# register new user admin
admin_site.register(User, UserAdmin)
admin_site.register(Group)
admin_site.register(UserProfile)
admin_site.register(Individual, IndividualAdmin)
admin_site.register(Client,ClientAdmin)
admin_site.register(Contract)
admin_site.register(Bank)
admin_site.register(Currency)
admin_site.register(Bank_account)
admin_site.register(Country_of_residence)
admin_site.register(Request,RequestAdmin)
admin_site.register(Mission,MissionAdmin)
admin_site.register(Request_type,Request_typeAdmin)
admin_site.register(Mission_type,Mission_typeAdmin)
admin_site.register(Approval)
admin_site.register(Ordering)
admin_site.register(Payment_type)
admin_site.register(Additional_file)
admin_site.register(Role)
admin_site.register(Email_templates)
admin_site.register(History)
admin_site.register(celery_admin.PeriodicTask,celery_admin.PeriodicTaskAdmin)
admin_site.register(celery_admin.IntervalSchedule)
admin_site.register(celery_admin.CrontabSchedule)
admin_site.register(PushInformation)