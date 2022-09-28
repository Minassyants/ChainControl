from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Client, Contract, Bank, Currency, Bank_account, Request, Request_type, Approval, Ordering, Payment_type, Additional_file, Role,UserProfile, Email_templates, History
from django_celery_beat import admin as celery_admin

class MyAdminSite(admin.AdminSite):
    site_header = 'CC administration'
    site_title = 'CC admin'

admin_site = MyAdminSite(name='CC')



class OrderingInline(admin.TabularInline):
    model = Ordering
    extra = 1

class Bank_accountInline(admin.TabularInline):
    model = Bank_account
    extra = 0

class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0

class Additional_fileInline(admin.TabularInline):
    model = Additional_file
    extra = 0

class Request_typeAdmin(admin.ModelAdmin):
    inlines = [OrderingInline]
    search_fields = ['name']

class ClientAdmin(admin.ModelAdmin):
    inlines = [ContractInline,Bank_accountInline]
    list_display = ('name','biin')
    search_fields = ['name','biin']

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
   


# unregister old user admin
#admin_site.unregister(User)
# register new user admin
admin_site.register(User, UserAdmin)
admin_site.register(Group)
admin_site.register(UserProfile)
admin_site.register(Client,ClientAdmin)
admin_site.register(Contract)
admin_site.register(Bank)
admin_site.register(Currency)
admin_site.register(Bank_account)
admin_site.register(Request,RequestAdmin)
admin_site.register(Request_type,Request_typeAdmin)
admin_site.register(Approval)
admin_site.register(Ordering)
admin_site.register(Payment_type)
admin_site.register(Additional_file)
admin_site.register(Role)
admin_site.register(Email_templates)
admin_site.register(History)
admin_site.register(celery_admin.PeriodicTask,celery_admin.PeriodicTaskAdmin)