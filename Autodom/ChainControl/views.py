from datetime import datetime, timedelta
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django import forms
from django.contrib import messages
from django.db.models import Q, F, Value, CharField,Count
from django.http import JsonResponse, HttpResponseForbidden
from .forms import RequestForm, AdditionalFileInlineFormset, ApprovalForm, RequestSearchForm
from .models import Request, Approval, Contract, Bank_account, Ordering, Additional_file, History,Client,Role,Request_type
from django.contrib.auth.models import User
from . import utils
from . import periodic_tasks
from . import russian_strings


@login_required
def index(request):
    #return render(request,'ChainControl/index.html')
    #r = integ_1C.getClients()
    return redirect('requests')


@login_required
def requests(request):
    cur_user = request.user
    webpush = {"user": cur_user }
    return render(request,'ChainControl/requests.html',{'webpush':webpush})

@login_required
def requesrs_to_be_done(request):
    #periodic_tasks.abc()
    cur_user = request.user
    approval_count = Count('approval')
    approved_count = Count('approval', filter = Q(approval__new_status = Request.StatusTypes.APPROVED))
    requests_list = Request.objects.annotate(approval_count = approval_count).annotate(approved_count = approved_count).filter(Q(status='AP') & Q(type__executor=cur_user.userprofile.role)).distinct()
    #Search query
    ALLOWED = ('id', 'client', 'sum','date','user','status')
    request_filter = RequestSearchForm(request.GET)
    if request_filter.is_valid():
        kwargs = dict(
            (key, value)
            for key, value in request_filter.cleaned_data.items()
            if key in ALLOWED and (value != None and value != "")
        )
        requests_list = requests_list.filter(**kwargs)

    utils.set_approval_color(requests_list)

    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page')
    requests_list = paginator.get_page(page_number)
  
    return render(request,'ChainControl/requests_to_be_done.html',{'requests':requests_list})

@login_required
def requests_for_approval(request):
    cur_user = request.user
    approval_count = Count('approval')
    approved_count = Count('approval', filter = Q(approval__new_status = Request.StatusTypes.APPROVED))
    requests_list = Request.objects.annotate(approval_count = approval_count).annotate(approved_count = approved_count).filter(Q(approval__new_status='OA') & (Q(approval__user=cur_user) | Q(approval__role=cur_user.userprofile.role))).distinct()
    ALLOWED = ('id', 'client', 'sum','date','user','status')
    request_filter = RequestSearchForm(request.GET)
    if request_filter.is_valid():
        kwargs = dict(
            (key, value)
            for key, value in request_filter.cleaned_data.items()
            if key in ALLOWED and (value != None and value != "")
        )
        requests_list = requests_list.filter(**kwargs)    
    utils.set_approval_color(requests_list)

    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page')
    requests_list = paginator.get_page(page_number)

    return render(request,'ChainControl/requests_for_approval.html',{'requests':requests_list})

@login_required
def requests_all(request):
    
    approval_count = Count('approval')
    approved_count = Count('approval', filter = Q(approval__new_status = Request.StatusTypes.APPROVED))
    requests_list = Request.objects.all().annotate(approval_count = approval_count).annotate(approved_count = approved_count)

    #Search query
    ALLOWED = ('id', 'client', 'sum','date','user','status')
    request_filter = RequestSearchForm(request.GET)
    if request_filter.is_valid():
        kwargs = dict(
            (key, value)
            for key, value in request_filter.cleaned_data.items()
            if key in ALLOWED and (value != None and value != "")
        )
        requests_list = requests_list.filter(**kwargs)

    ##Ordering 
    #if 'o' in request.GET:
    #    order_params = request.GET['o'].split('.')
    #    for p in order_params:
    #        try:
    #            none, pfx, idx = p.rpartition('-')

    #        except (IndexError, ValueError):
    #            continue


    utils.set_approval_color(requests_list)

    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page')
    requests_list = paginator.get_page(page_number)

    return render(request,'ChainControl/requests_all.html',{'requests':requests_list})

@login_required
def requests_my_requests(request):
    if request.method == 'GET':
        cur_user = request.user
        approval_count = Count('approval')
        approved_count = Count('approval', filter = Q(approval__new_status = Request.StatusTypes.APPROVED))
        requests_list = Request.objects.filter(user=cur_user).annotate(approval_count = approval_count).annotate(approved_count = approved_count)
        ALLOWED = ('id', 'client', 'sum','date','user','status')
        request_filter = RequestSearchForm(request.GET)
        if request_filter.is_valid():
            kwargs = dict(
                (key, value)
                for key, value in request_filter.cleaned_data.items()
                if key in ALLOWED and (value != None and value != "")
            )
            requests_list = requests_list.filter(**kwargs)
        utils.set_approval_color(requests_list)

        paginator = Paginator(requests_list, 10)
        page_number = request.GET.get('page')
        requests_list = paginator.get_page(page_number)

        return render(request,'ChainControl/requests_my_requests.html',{'requests':requests_list})
    raise PermissionDenied

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
            if addfiles.is_valid():
                files = addfiles.save(commit = False)
                for file in files:
                    file.request_1 = obj
                    file.save()
                messages.success(request,'Заявка создана')
                return redirect('index')
            else:
                messages.warning(request,'Заявка создана, но файлы не загружены')
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
                                                                 "addfiles":addfiles,
                                                                 })
@login_required
def request_item(request, id):
    el = get_object_or_404(Request,id=id)
    user_is_owner = el.user == request.user
    approving_user = el.approval_set.filter(new_status='OA').order_by('order')[:1]
    if el.status != Request.StatusTypes.ON_REWORK and approving_user.count() > 0 :
        approving_user = approving_user.get()
        if (approving_user.user != None and approving_user.user == request.user) or (approving_user.role != None and approving_user.role == request.user.userprofile.role) :
            approving_user = approving_user.id
        else:
            approving_user = False
    else:
       approving_user = False

    user_is_executor = request.user.userprofile.role == el.type.executor and el.status == Request.StatusTypes.APPROVED

    modelformset = modelformset_factory(Additional_file,fields='__all__',extra=3,can_delete=True,max_num=3)
    
    if request.method == 'POST':
        form = RequestForm(request.POST, instance=el)
        addfiles = modelformset(request.POST,request.FILES,initial=[{
            'request_1':el,},])
        if not user_is_owner:
            messages.warning(request,'Заявка редактируется только заявителем')
        else:
            if form.is_valid():
                obj = form.save(commit = False)
                if len(form.changed_data) > 0 :
                    if obj.status == Request.StatusTypes.ON_REWORK:
                        obj.status == Request.StatusTypes.ON_APPROVAL
                        utils.write_history(obj,request.user,Request.StatusTypes.ON_APPROVAL, russian_strings.comment_request_reworked)
                    else :
                        utils.write_history(obj,request.user,Request.StatusTypes.ON_APPROVAL, russian_strings.comment_request_changed)
                    obj.user = request.user
                    utils.reset_request_approvals(obj)
                    obj.save()
                    periodic_tasks.send_approval_status_approved_notification(obj)
                    
                if addfiles.is_valid():
                    files = addfiles.save(commit = False)
                    for file in addfiles.deleted_objects:
                        file.delete()
                    for file in files:
                        file.request_1 = obj
                        file.save()
                    messages.success(request,'Заявка обновлена')
                    #return redirect('index')
                else:
                    messages.warning(request,'Заявка обновлена, но файлы не изменены')
                    #return redirect('index')
    else:
        if user_is_owner:
            form = RequestForm(None,instance=el)
        else:
            form = el
        addfiles = modelformset(queryset=Additional_file.objects.filter(request_1=el.id),initial=[{
                'request_1':el,},])
       
        
    history = History.objects.filter(request = el).order_by('date')
    utils.set_approval_color(history)
    return render(request,'ChainControl/request_item.html',{"form" : form,
                                                            "addfiles": addfiles,
                                                            "user_is_owner" : user_is_owner,
                                                            "approving_user" : approving_user,
                                                            "history" : history,
                                                            "request_status" : el.get_status_display(),
                                                            "user_is_executor": user_is_executor,
                                                            })

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
def get_clients(request):
    if request.method == 'GET':
        
        els = list(Client.objects.all().values('id','name').annotate(value=F('id'),text=F('name')))
        return JsonResponse(els, safe=False)

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
@login_required
def get_approval_status(request):
    if request.method == 'GET':
        id = request.GET['id']
        els = Approval.objects.filter(request__id = id).order_by('order').annotate(color=Value('xxx', output_field=CharField()))
        utils.set_approval_color(els)
        return render(request,'ChainControl/approval_status.html',{"els":els})

@login_required
def get_approval_form(request,id):
    el = get_object_or_404(Approval,id=id)
    if request.method == 'POST':
        form = ApprovalForm(request.POST,instance=el)
        if form.is_valid() and 'new_status' in form.changed_data:
            obj = form.save(commit=False)
            obj.user = request.user
            form.save()
            messages.success(request,'Статус заявки изменен')
        else:
            messages.warning(request,'Не удалось изменить статус')
        return redirect('index')
    else:
        
        form = ApprovalForm(instance=el)
        if el.user != None:
            if el.user == request.user:
                context = {
                    "form": form,
                }
        elif el.role == request.user.userprofile.role:
            context = {
                    "form":form,
                }
    return render(request,'ChainControl/approval_form.html',context)

@login_required
def get_search_form(request):
    form = RequestSearchForm()
    return render(request,'ChainControl/request_search_form.html', {
        'form' : form 
        })

@login_required
def set_request_done(request, id):
    if request.method == 'POST' and 'done' in request.POST:
        el = get_object_or_404(Request,id=id)
        if el.status == Request.StatusTypes.APPROVED and el.type.executor == request.user.userprofile.role:
            el.status = Request.StatusTypes.DONE
            el.save()
            utils.write_history(el,request.user,el.status, russian_strings.comment_request_done)
            periodic_tasks.send_request_done_notification(el)
        return redirect(reverse('request_item', args=[str(el.id)]))
    raise PermissionDenied

@login_required
def set_request_canceled(request, id):
    if request.method == 'POST' and 'cancel' in request.POST:
        el = get_object_or_404(Request,id=id)
        NOT_ALLOWED = {Request.StatusTypes.DONE}
        if  not el.status in NOT_ALLOWED and el.user == request.user:
            el.status = Request.StatusTypes.CANCELED
            el.save()
            utils.reset_request_approvals(el)
            messages.success(request,'Заявка отменена')
            utils.write_history(el,request.user,el.status, russian_strings.comment_request_canceled)
            periodic_tasks.send_request_canceled_notification(el)
        return redirect(reverse('request_item', kwargs={"pk":str(el.id)}))
    raise PermissionDenied

@method_decorator(login_required,name='dispatch')
class RequestDetailView(DetailView):
    model = Request
    form_class = RequestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['user_is_executor'] = self.request.user.userprofile.role == self.object.type.executor and self.object.status == Request.StatusTypes.APPROVED

        DISALOWED_STATUS = [ Request.StatusTypes.DONE, Request.StatusTypes.CANCELED ]
        context['user_can_cancel'] = self.request.user == self.object.user and not self.object.status in DISALOWED_STATUS

        history = self.object.history_set.order_by('-date')
        utils.set_approval_color(history)
        context['history'] = history

        approving_user = self.object.approval_set.filter(new_status='OA',request__status = 'OA').order_by('order')[:1]
        if self.object.status != Request.StatusTypes.ON_REWORK and approving_user.count() > 0 :
            approving_user = approving_user.get()
            if (approving_user.user != None and approving_user.user == self.request.user) or (approving_user.role != None and approving_user.role == self.request.user.userprofile.role) :
                approving_user = approving_user.id
            else:
                approving_user = False
        else:
           approving_user = False
        context['approving_user'] = approving_user

        return context

    def render_to_response(self, context):
        ALOWED_STATUS = [Request.StatusTypes.APPROVED, Request.StatusTypes.DONE]
        if self.object.user == self.request.user and not self.object.status in ALOWED_STATUS  :
            return redirect('request_update',pk=self.object.pk)
        return super(RequestDetailView,self).render_to_response(context)


@method_decorator(login_required,name='dispatch')
class RequestUpdateView(UpdateView):
    model = Request
    form_class = RequestForm

    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)

        DISALOWED_STATUS = [ Request.StatusTypes.DONE, Request.StatusTypes.CANCELED ]
        context['user_can_cancel'] = self.request.user == self.object.user and not self.object.status in DISALOWED_STATUS

        history = self.object.history_set.order_by('-date')
        utils.set_approval_color(history)
        context['history'] = history

        modelformset = modelformset_factory(Additional_file,fields='__all__',extra=3,can_delete=True,max_num=3)
        addfiles = modelformset(queryset=Additional_file.objects.filter(request_1=self.object.id),initial=[{
                'request_1':self.object,},])
        context['addfiles'] = addfiles

        return context

    def post(self, request, **kwargs):
        self.object = self.get_object()
        if request.user != self.object.user:
            messages.warning(request,'Заявка редактируется только заявителем')
            return HttpResponseForbidden

        form = self.get_form()
        modelformset = modelformset_factory(Additional_file,fields='__all__',extra=3,can_delete=True,max_num=3)
        addfiles = modelformset(request.POST,request.FILES,initial=[{
            'request_1':self.object,},])
        if addfiles.is_valid():
            files = addfiles.save(commit = False)
            for file in addfiles.deleted_objects:
                file.delete()
            for file in files:
                file.request_1 = self.object
                file.save()
        
        
        if form.data['status'] == Request.StatusTypes.ON_REWORK or form.data['status']== Request.StatusTypes.CANCELED:
            form.data._mutable = True
            form.data['status'] = Request.StatusTypes.ON_APPROVAL
            form.data._mutable = False
            comment = russian_strings.comment_request_reworked    
        else :
            comment = russian_strings.comment_request_changed
            
        if form.is_valid():
            if len(form.changed_data) > 0:
                utils.write_history(self.object,request.user,Request.StatusTypes.ON_APPROVAL, comment)
                utils.reset_request_approvals(self.object)
                messages.success(request,'Заявка обновлена')
            periodic_tasks.send_approval_status_approved_notification(self.object)
            return self.form_valid(form)
        else:
            messages.warning(request,'Не удалось обновить заявку')
            return self.form_invalid(form)

    def render_to_response(self, context):
        DISALOWED_STATUS = [Request.StatusTypes.APPROVED, Request.StatusTypes.DONE]
        if self.object.user != self.request.user or self.object.status in DISALOWED_STATUS :
            return redirect('request_item',pk=self.object.pk)
        return super(RequestUpdateView,self).render_to_response(context)

@method_decorator(login_required,name='dispatch')
class RequestListView(ListView):
    model= Request
    paginate_by = 20

    def get_queryset(self):
        cur_user = self.request.user
        approval_count = Count('approval')
        approved_count = Count('approval', filter = Q(approval__new_status = Request.StatusTypes.APPROVED))
        qs = super(RequestListView, self).get_queryset().annotate(approval_count = approval_count).annotate(approved_count = approved_count)

        mode = self.request.GET.get('mode','requests_for_approval')
        
        if mode == 'my_requests':
            qs = qs.filter(user=cur_user)
        elif mode == 'requests_to_be_done':
            qs =qs.filter(Q(status='AP') & Q(type__executor=cur_user.userprofile.role)).distinct()
        elif mode == 'all_requests' and cur_user.is_staff:
            pass
        else:
            qs = qs.filter(Q(approval__new_status='OA', approval__request__status='OA') & (Q(approval__user=cur_user) | Q(approval__role=cur_user.userprofile.role))).distinct()

        ALLOWED = ('id', 'client', 'sum','date','user','status')
        request_filter = RequestSearchForm(self.request.GET)
        if request_filter.is_valid():
            kwargs = dict(
                (key, value)
                for key, value in request_filter.cleaned_data.items()
                if key in ALLOWED and (value != None and value != "")
            )
            if request_filter.cleaned_data['expired']:
                kwargs['status__in'] = ['OA','AP']
                kwargs['complete_before__lte'] = datetime.now()
            qs = qs.filter(**kwargs)


        qs = qs.order_by('-id')
        utils.set_approval_color(qs)
        return qs
@method_decorator(login_required,name='dispatch')
class RequestCreateView(CreateView):
    model = Request
    form_class = RequestForm
    template_name_suffix = '_create_form'
    

    def get_initial(self):
        now = datetime.now()
        return {'user':self.request.user,
                'date':now.date,
                'complete_before': now+timedelta( days= 3),
                'invoice_date':now,
                'AVR_date':now,
                'status':Request.StatusTypes.ON_APPROVAL.value,
                }

    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        context['addfiles'] = AdditionalFileInlineFormset()
        return context

    def post(self, request, *args, **kwargs):
        form = RequestForm(request.POST)        
        addfiles = AdditionalFileInlineFormset(request.POST,request.FILES, instance=form.instance)
        # check whether it's valid:
        if form.is_valid() :
            obj = form.save(commit = False)
            obj.user = request.user
            form.save()
            if addfiles.is_valid():
                files = addfiles.save(commit = False)
                for file in files:
                    file.request_1 = obj
                    file.save()
                messages.success(request,'Заявка создана')
                return self.form_valid(form)
            
        messages.warning(request,'Заявка не создана')

        return self.form_invalid(form)

def test_view(request):
    approval_roles_1 = Role.objects.filter(approval__new_status='OA', approval__request__status='OA')
    approval_users_1 = User.objects.filter(Q(approval__new_status='OA', approval__request__status='OA') | Q(userprofile__role__in = approval_roles_1 )).distinct()

    approval_roles_2 = Role.objects.filter(approval__new_status='OA',approval__request__status='OA', approval__request__complete_before__lte = datetime.now() )
    approval_users_2 = User.objects.filter(Q(approval__new_status='OA', approval__request__status='OA', approval__request__complete_before__lte = datetime.now() ) | Q(userprofile__role__in = approval_roles_2 )).distinct()

    approval_roles_3 = Request_type.objects.filter(request__status='AP').values('executor')
    approval_users_3 = User.objects.filter(Q(userprofile__role__in = approval_roles_3 )).distinct()

    return render(request,'ChainControl/t1.html',{
        "u1" : approval_users_1,
        "u2" : approval_users_2,
        "u3" : approval_users_3,
        })