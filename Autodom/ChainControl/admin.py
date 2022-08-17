from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import Client, Contract, Bank, Currency, Bank_account, Request, Request_type, Approval, Ordering, Payment_type, Additional_file, Role,UserProfile, Email_templates, History

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
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)

admin.site.register(UserProfile)
admin.site.register(Client,ClientAdmin)
admin.site.register(Contract)
admin.site.register(Bank)
admin.site.register(Currency)
admin.site.register(Bank_account)
admin.site.register(Request,RequestAdmin)
admin.site.register(Request_type,Request_typeAdmin)
admin.site.register(Approval)
admin.site.register(Ordering)
admin.site.register(Payment_type)
admin.site.register(Additional_file)
admin.site.register(Role)
admin.site.register(Email_templates)
admin.site.register(History)