from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django import forms
from django.contrib import messages
from django.db.models import Q, F, Value, CharField
from .forms import RequestForm, AdditionalFileInlineFormset
from .models import Request, Approval, Contract, Bank_account, Ordering
from django.http import JsonResponse
import Autodom.integ_1C as integ_1C
from . import utils
from pwa_webpush import send_group_notification




@login_required
def index(request):
    #return render(request,'ChainControl/index.html')
    #r = integ_1C.getClients()
    return redirect('requests')


@login_required
def requests(request):
    cur_user = request.user
    webpush = {"group": 'name' }
    return render(request,'ChainControl/requests.html',{'webpush':webpush})

@login_required
def requests_for_approval(request):
    cur_user = request.user
    requests_list = Request.objects.filter(Q(approval__new_status='OA') & (Q(approval__user=cur_user) | Q(approval__role=cur_user.userprofile.role))).distinct()
    return render(request,'ChainControl/requests_for_approval.html',{'requests':requests_list})

@login_required
def requests_all(request):
    
    payload = {"head": "Welcome!", "body": "Hello World"}

    send_group_notification(group_name="name", payload=payload, ttl=1000)

    requests_list = Request.objects.all()
    return render(request,'ChainControl/requests_all.html',{'requests':requests_list})

@login_required
def requests_my_requests(request):
    cur_user = request.user
    requests_list = Request.objects.filter(user=cur_user)
    return render(request,'ChainControl/requests_my_requests.html',{'requests':requests_list})

@login_required
def createRequest(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        addfiles = AdditionalFileInlineFormset(request.POST,request.FILES, instance=form.instance)
        # check whether it's valid:
        if form.is_valid() :
            obj = form.save(commit = False)
            obj.user = request.user
            form.save()
            files = addfiles.save(commit = False)
            for file in files:
                file.request_1 = obj
                file.save()
            messages.success(request,'Заявка создана')
            return redirect('index')
    else:
        now = datetime.now()
        form = RequestForm(initial={
            'user':request.user,
            'date':now.date,
            'complete_before': now+timedelta( days= 3),
            'invoice_date':now,
            'AVR_date':now,
            'status':Request.StatusTypes.ON_APPROVAL.value,
            })
       
        addfiles = AdditionalFileInlineFormset()
        return render(request,"ChainControl/createRequest.html",{"form":form,
                                                                 "addfiles":addfiles})

def request_item(request, id):
    el = get_object_or_404(Request,id=id)
    if request.method == 'POST':
        form = RequestForm(request.POST, instance=el)
    else:
        form = RequestForm(instance=el)
    return render(request,'ChainControl/request_item.html',{"form":form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user1 = authenticate(request, username=username, password=password)
        if user1 is not None:
            login(request, user1)
            # Redirect to a success page.
            return redirect('index')
        else:
            messages.success(request,'Ошибка входа')
            return redirect('login_user')
            # Return an 'invalid login' error message.
    form = AuthenticationForm()
    form.fields['username'].widget = forms.TextInput(attrs={'autofocus': True,
                                                         'class' : 'form-control',
                                                         })
    form.fields['password'].widget = forms.PasswordInput(attrs={'class' : 'form-control',
                                                         })
    context = {
        'form' : form,
        'next' : request.GET.get('next'),
        }
    a = render(request,'ChainControl/login_user.html',context)
    return a

def logout_user(request):
    logout(request)
    return redirect('login_user')

@login_required
def get_contracts(request):
    if request.method == 'GET':
        id = request.GET['id']
        els = list(Contract.objects.filter(client__id = id).values('id','name').annotate(value=F('id'),text=F('name')))
        return JsonResponse(els, safe=False)

@login_required
def get_bank_accounts(request):
    if request.method == 'GET':
        id = request.GET['id']
        els = list(Bank_account.objects.filter(client__id = id).values('id','account_number').annotate(value=F('id'),text=F('account_number')))
        return JsonResponse(els, safe=False)

@login_required
def get_ordering_for_new_request(request):
    if request.method == 'GET':
        id = request.GET['id']
        els = Ordering.objects.filter(request_type__id = id).order_by('order')
        ordering = []
        for el in els:
            if el.user != None:
                ordering.append(el.user.first_name)
            else:
                ordering.append(el.role.name)
        return render(request,'ChainControl/ordering_for_new_request.html',{"ordering":ordering})

def get_approval_status(request):
    if request.method == 'GET':
        id = request.GET['id']
        els = Approval.objects.filter(request__id = id).order_by('order').annotate(color=Value('xxx', output_field=CharField()))
        utils.set_approval_color(els)
        return render(request,'ChainControl/approval_status.html',{"els":els})