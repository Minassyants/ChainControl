import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django import forms
from django.contrib import messages
from django.db.models import Q
from .forms import RequestForm, AdditionalFileInlineFormset
from .models import Request, Approval

import Autodom.integ_1C as integ_1C

@login_required
def index(request):
    #return render(request,'ChainControl/index.html')
    #r = integ_1C.getClients()
    return redirect('requests')


@login_required
def requests(request):
    cur_user = request.user
    return render(request,'ChainControl/requests.html')

@login_required
def requests_for_approval(request):
    cur_user = request.user
    requests_list = Request.objects.filter(Q(approval__is_approved=False) & (Q(approval__user=cur_user) | Q(approval__role=cur_user.userprofile.role))).distinct()
    return render(request,'ChainControl/requests_for_approval.html',{'requests':requests_list})

@login_required
def requests_all(request):
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
            form.save()
            files = addfiles.save(commit = False)
            for file in files:
                file.request_1 = obj
                file.save()
            messages.success(request,'Заявка создана')
            return redirect('index')
    else:
        now = datetime.datetime.now()
        form = RequestForm(initial={
            'user':request.user,
            'complete_before': now+datetime.timedelta( days= 3),
            'invoice_date':now,
            'AVR_date':now})
       
        addfiles = AdditionalFileInlineFormset()
        return render(request,"ChainControl/createRequest.html",{"form":form,
                                                                 "addfiles":addfiles})

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
