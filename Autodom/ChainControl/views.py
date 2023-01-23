from datetime import datetime
import base64
from io import BytesIO
import jwt
import xlsxwriter
from operator import attrgetter
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django import forms
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F, Value, CharField,Count
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import qrcode
from itertools import chain
from Autodom import settings
from .forms import RequestForm, MissionForm, AdditionalFileInlineFormset, ApprovalForm, RequestSearchForm, MissionSearchForm, List_to_excelForm
from .models import Request, Request_type, Approval, Contract, Bank_account, Ordering, Additional_file, Client, Individual, Individual_bank_account, Mission, Mission_type
from . import utils
from . import periodic_tasks
from . import russian_strings


@login_required
def tg_get_auth_qrcode(request):
    img = qrcode.make(f'https://t.me/ChainControl_bot?start={request.user.username}')
    buff = BytesIO()
    img.save(buff, format="PNG")
    img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
    context = {"qrcode":img_str}
    temp = render(request,'ChainControl/tg_qrcode.html',context)

    

    return temp

@csrf_exempt
def tg_logout(request):
    if request.method == 'POST':
        response = {'value':False}
        try:
            user = User.objects.get(userprofile__tg_chat_id=int(request.POST['chat_id']))
        except:
            response['error'] = "User not found"
            return JsonResponse(response)
        user.userprofile.tg_chat_id = None
        user.userprofile.save()
        response['value'] = True
        return JsonResponse(response)
    return PermissionDenied

@csrf_exempt
def tg_reg_user(request):
    if request.method == 'POST':
        response = {'value':False}
        try:
            user = User.objects.get(username=request.POST['username'])
        except:
            response['error'] = "User not found"
            return JsonResponse(response)

        if user.check_password(request.POST['password']):
            for u in User.objects.filter(~Q(id=user.id),userprofile__tg_chat_id=int(request.POST['chat_id'])):
                u.userprofile.tg_chat_id = None
                u.userprofile.save()
            user.userprofile.tg_chat_id = int(request.POST['chat_id'])
            user.userprofile.save()
            response['value'] = True
            return JsonResponse(response)

        response['error'] = "Password is incorrect"
        return JsonResponse(response)
    return None

@login_required
def get_sd_token(request):
    if request.method == 'GET':
        header = {
        "alg": "HS256",
        "typ": "JWT"
        };
        payload = {
            "email": request.user.email,
            "displayName": f"{request.user.last_name} {request.user.first_name}",
            "iat": datetime.now().timestamp() ,
            "exp": datetime.now().timestamp() + 60 * 5
            }
        encoded_jwt = jwt.encode(payload,settings.SD_SECRET, algorithm="HS256", headers=header)
        return HttpResponse(encoded_jwt)
    return HttpResponseForbidden("Forbidden!")

@login_required
def list_to_excel(request):
    if request.method == 'GET':

            cur_user = request.user
            approval_count = Count('approval')
            approved_count = Count('approval', filter = Q(approval__new_status = Request.StatusTypes.APPROVED))
            if request.GET['type'] == 'mission':
                qs = Mission.objects.all().annotate(approval_count = approval_count).annotate(approved_count = approved_count)
                qs =qs.filter(Q(status='AP') & Q(type__requestexecutor__role=cur_user.userprofile.role)).distinct()
                qs = qs.order_by('-id')
                utils.set_approval_color(qs)
            elif request.GET['type'] == 'request':

                qs = Request.objects.all().annotate(approval_count = approval_count).annotate(approved_count = approved_count)
                qs =qs.filter(Q(status='AP') & Q(type__requestexecutor__role=cur_user.userprofile.role)).distinct()
                qs = qs.order_by('-id')
                utils.set_approval_color(qs)
            else:
                models_list = [Request, Mission]
                q_list = []
                
                #qs =qs.filter(Q(status='AP') & Q(type__requestexecutor__role=cur_user.userprofile.role)).distinct()
                for m in models_list:
                    v_n = m._meta.verbose_name
                    q_list.append( m.objects.filter( Q(status='AP') & Q(type__requestexecutor__role=cur_user.userprofile.role) ).distinct().annotate(approval_count = approval_count).annotate(approved_count = approved_count).annotate(model_name=Value(v_n, output_field=CharField())) )
                for q in q_list:
            
                    utils.set_approval_color(q)

                qs = sorted( list(chain(*q_list)), key=attrgetter('date') , reverse= True  )

           
        
            qs = list(qs)
            
            buffer = BytesIO()
            workbook = xlsxwriter.Workbook(buffer)
            worksheet = workbook.add_worksheet()
            worksheet.write(0,0, '#')
            worksheet.write(0,1, 'Тип Заявки')
            worksheet.write(0,2, 'Автор')
            worksheet.write(0,3, 'Контрагент/Физ. Лицо')
            worksheet.write(0,4, 'Сумма')
            worksheet.write(0,5, 'Валюта')
            worksheet.write(0,6, 'Статус')
            i = 1
            for val in qs:
                if type(val) == Request:
                    if val.individual != None and val.individual !="":
                        client = val.individual
                    else:
                        client = val.client
                    doc_sum = val.sum
                    currency = val.currency.code_str
                elif type(val) == Mission:
                    client = val.individual
                    doc_sum = (val.cost_of_living if val.cost_of_living is not None else 0) + (val.daily_allowance if val.daily_allowance is not None else 0) + (val.ticket_price if val.ticket_price is not None else 0)
                    currency = "KZT"

                worksheet.write(i,0, val.id)
                worksheet.write(i,1, val._meta.verbose_name.title())
                worksheet.write(i,2, val.user.last_name + " " + val.user.first_name[0] + ".")
                worksheet.write(i,3, str(client))
                worksheet.write(i,4, doc_sum)
                worksheet.write(i,5, currency)
                worksheet.write(i,6, val.get_status_display())
                i+=1
            workbook.close()
            buffer.seek(0)
            
            return FileResponse(buffer, as_attachment=True, filename=f'Список заявок {datetime.now()}.xlsx')

    return HttpResponseForbidden("Forbidden!")
@login_required
def index(request):
    return redirect('all_requests')

@login_required
def docs(request):
    return render(request,'ChainControl/docs/guide_list.html')

@login_required
def create(request):
    return render(request,'ChainControl/docs/create.html')

@login_required
def approval(request):
    return render(request,'ChainControl/docs/approval.html')

@login_required
def execution(request):
    return render(request,'ChainControl/docs/execution.html')

@login_required
def request_description(request):
    return render(request,'ChainControl/docs/request_description.html')

@login_required
def main_screen_description(request):
    return render(request,'ChainControl/docs/main_screen_description.html')

@login_required
def app_description(request):
    return render(request,'ChainControl/docs/app_description.html')

@login_required
def request_life_cycle(request):
    return render(request,'ChainControl/docs/request_life_cycle.html')

@login_required
def missions(request):
    cur_user = request.user
    webpush = {"user": cur_user }
    return render(request,'ChainControl/missions.html',{'webpush':webpush})


@login_required
def requests(request):
    cur_user = request.user
    webpush = {"user": cur_user }
    return render(request,'ChainControl/requests.html',{'webpush':webpush})

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
def get_individuals(request):
    if request.method == 'GET':
        
        els = list(Individual.objects.all().values('id','name').annotate(value=F('id'),text=F('name')))
        return JsonResponse(els, safe=False)

@login_required
def get_clients(request):
    if request.method == 'GET':
        
        els = list(Client.objects.all().values('id','name').annotate(value=F('id'),text=F('name')))
        return JsonResponse(els, safe=False)

@login_required
def get_contracts(request):
    if request.method == 'GET':
        id = request.GET['id']
        if id == "":
            return JsonResponse([], safe=False)
        els = list(Contract.objects.filter(client__id = id).values('id','name').annotate(value=F('id'),text=F('name')))
        return JsonResponse(els, safe=False)

@login_required
def get_individual_bank_accounts(request):
    if request.method == 'GET':
        id = request.GET['id']
        if id == "":
            return JsonResponse([], safe=False)
        els = list(Individual_bank_account.objects.filter(individual__id = id).values('id','account_number').annotate(value=F('id'),text=F('account_number')))
        return JsonResponse(els, safe=False)

@login_required
def get_bank_accounts(request):
    if request.method == 'GET':
        id = request.GET['id']
        if id == "":
            return JsonResponse([], safe=False)
        els = list(Bank_account.objects.filter(client__id = id).values('id','account_number').annotate(value=F('id'),text=F('account_number')))
        return JsonResponse(els, safe=False)

@login_required
def get_ordering_for_new_request(request):
    if request.method == 'GET':
        id = request.GET.get('id','')
        model_id = request.GET.get('model_id','')
        ordering = []
        if id != '' and model_id != '':
            els = Ordering.objects.filter(content_type=model_id,object_id=id).order_by('order')
            for el in els:
                if el.user != None:
                    ordering.append(f'{el.user.last_name} {el.user.first_name[0]}.')
                else:
                    ordering.append(el.role.name)
        else:
            ordering.append('Выберите вид заявки.')
        
       
        return render(request,'ChainControl/ordering_for_new_request.html',{"ordering":ordering})
    
@login_required
def get_approval_status(request):
    if request.method == 'GET':
        id = request.GET['id']
        model_id = request.GET['model_id']
        els = Approval.objects.filter(content_type=model_id,object_id = id).order_by('order').annotate(color=Value('xxx', output_field=CharField()))
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

        if obj.content_type == ContentType.objects.get_for_model(Request).id:
            return redirect('requests')
        else:
            return redirect('missions')
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
def get_all_requests_search_form(request):
    form = RequestSearchForm()
    return render(request,'ChainControl/all_requests_search_form.html', {
        'form' : form 
        })

@login_required
def get_mission_search_form(request):
    form = MissionSearchForm()
    return render(request,'ChainControl/mission_search_form.html', {
        'form' : form 
        })

@login_required
def get_search_form(request):
    form = RequestSearchForm()
    return render(request,'ChainControl/request_search_form.html', {
        'form' : form 
        })

@login_required
def set_request_done(request, model_id,id):
    if request.method == 'POST' and 'done' in request.POST:
        model = ContentType.objects.get(id=model_id)
        el = get_object_or_404(model.model_class(),id=id)
        if el.status == Request.StatusTypes.APPROVED and el.type.requestexecutor.filter(role = request.user.userprofile.role).exists() :
            el.status = Request.StatusTypes.DONE
            el.save()
            utils.write_history(el,request.user,el.status, russian_strings.comment_request_done)
            periodic_tasks.send_request_done_notification(el)
        return redirect(reverse(f'{model.model.lower()}_item', args=[str(el.id)]))
    raise PermissionDenied

@login_required
def set_request_canceled(request, model_id, id):
    if request.method == 'POST' and 'cancel' in request.POST:
        model = ContentType.objects.get(id=model_id)
        el = get_object_or_404(model.model_class(),id=id)
        NOT_ALLOWED = {Request.StatusTypes.DONE}
        if  not el.status in NOT_ALLOWED and el.user == request.user:
            el.status = Request.StatusTypes.CANCELED
            el.save()
            utils.reset_request_approvals(el)
            messages.success(request,'Заявка отменена')
            utils.write_history(el,request.user,el.status, russian_strings.comment_request_canceled)
            periodic_tasks.send_request_canceled_notification(el)
        return redirect(reverse(f'{model.model.lower()}_item', kwargs={"pk":str(el.id)}))
    raise PermissionDenied

@login_required
def request_print(request,model_id,pk):
    model = ContentType.objects.get(id=model_id)
    obj = get_object_or_404(model.model_class(),pk=pk)
    els = obj.approval.order_by('order')
    context = {
        "object":obj,
        "els":els,
        "company_name": settings.COMPANY_NAME,
        }
    return render(request,f'ChainControl/{model.model.lower()}_print.html',context)


@method_decorator(login_required,name='dispatch')
class RequestDetailView(DetailView):
    model = Request
    form_class = RequestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['user_is_executor'] = self.object.type.requestexecutor.filter(role=self.request.user.userprofile.role).exists() and self.object.status == Request.StatusTypes.APPROVED
        #context['user_is_executor'] = self.object.type.requestexecutor_set.filter(role=self.request.user.userprofile.role).exists() and self.object.status == Request.StatusTypes.APPROVED

        DISALOWED_STATUS = [ Request.StatusTypes.DONE, Request.StatusTypes.CANCELED ]
        context['user_can_cancel'] = self.request.user == self.object.user and not self.object.status in DISALOWED_STATUS

        history = self.object.history.order_by('-date')
        #history = self.object.history_set.order_by('-date')
        utils.set_approval_color(history)
        context['history'] = history
        context['model_id'] = ContentType.objects.get_for_model(self.object).id
        if self.object.status == 'OA':
            approving_user = self.object.approval.filter(new_status='OA').order_by('order')[:1]
        else:
            approving_user = Approval.objects.none()
        #approving_user = self.object.approval_set.filter(new_status='OA',request__status = 'OA').order_by('order')[:1]
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

        history = self.object.history.order_by('-date')
        #history = self.object.history_set.order_by('-date')
        utils.set_approval_color(history)
        context['history'] = history

        modelformset = modelformset_factory(Additional_file,fields='__all__',extra=3,can_delete=True,max_num=3)
        ticket_type = ContentType.objects.get_for_model(self.object).id
        addfiles = modelformset(queryset=Additional_file.objects.filter(content_type=ticket_type,object_id=self.object.id),initial=[{
                'content_type':ticket_type,
                'object_id':self.object.id},])
        context['addfiles'] = addfiles
        context['model_id'] = ticket_type
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
            qs =qs.filter(Q(status='AP') & Q(type__requestexecutor__role=cur_user.userprofile.role)).distinct()
        elif mode == 'all_requests' and cur_user.is_staff:
            pass
        else:
            qs = qs.filter(Q(approval__new_status='OA', status='OA') & (Q(approval__user=cur_user) | Q(approval__role=cur_user.userprofile.role))).distinct()

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
                'complete_before': utils.next_weekday(now),
                'invoice_date':now,
                'AVR_date':now,
                'status':Request.StatusTypes.ON_APPROVAL.value,
                }

    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        context['addfiles'] = AdditionalFileInlineFormset()
        context['model_id'] = ContentType.objects.get_for_model(Request_type).id
        return context

    def post(self, request, *args, **kwargs):
        form = RequestForm(request.POST)        
        addfiles = AdditionalFileInlineFormset(request.POST,request.FILES, instance=form.instance)
        # check whether it's valid:
        if form.is_valid() :
            self.object = form.save(commit = False)
            self.object.user = request.user
            if self.object.is_accountable_person:
                if self.object.individual == None or (self.object.payment_type.cashless and self.object.individual_bank_account == None):
                    messages.warning(request,'Не заполнена информация о подотчетном лице.')
                    return self.form_invalid(self.get_form())
            else:
                if self.object.client == None or self.object.contract == None or (self.object.payment_type.cashless and self.object.bank_account == None):
                    messages.warning(request,'Не заполнена информация о контрагенте.')
                    return self.form_invalid(form)

            if self.object.currency == None:
                if self.object.contract != None and self.object.contract.currency != None:
                    self.object.currency = self.object.contract.currency
                else:
                    messages.warning(request,'В договоре не указана валюта. Необходимо указать валюту в заявке.')
                    return self.form_invalid(form)

            
            
            self.object.save()
            if addfiles.is_valid():
                files = addfiles.save(commit = False)
                for file in files:
                    file.request_1 = self.object
                    file.save()
                messages.success(request,'Заявка создана')
                return self.form_valid(form)
            
        messages.warning(request,'Заявка не создана')

        return self.form_invalid(form)


@method_decorator(login_required,name='dispatch')
class MissionListView(ListView):
    model= Mission
    paginate_by = 20

    def get_queryset(self):
        cur_user = self.request.user
        approval_count = Count('approval')
        approved_count = Count('approval', filter = Q(approval__new_status = Mission.StatusTypes.APPROVED))
        qs = super(MissionListView, self).get_queryset().annotate(approval_count = approval_count).annotate(approved_count = approved_count)

        mode = self.request.GET.get('mode','requests_for_approval')
        
        if mode == 'my_requests':
            qs = qs.filter(user=cur_user)
        elif mode == 'requests_to_be_done':
            qs =qs.filter(Q(status='AP') & Q(type__requestexecutor__role=cur_user.userprofile.role)).distinct()
        elif mode == 'all_requests' and cur_user.is_staff:
            pass
        else:
            qs = qs.filter(Q(approval__new_status='OA', status='OA') & (Q(approval__user=cur_user) | Q(approval__role=cur_user.userprofile.role))).distinct()

        ALLOWED = ('id', 'client', 'individual','date','user','status')
        request_filter = MissionSearchForm(self.request.GET)
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
class MissionCreateView(CreateView):
    model = Mission
    form_class = MissionForm
    template_name_suffix = '_create_form'
    


    def get_initial(self):
        now = datetime.now()
        return {'user':self.request.user,
                'date':now.date,
                'complete_before': utils.next_weekday(now),
                'date_from':now,
                'date_to':now,
                'status':Request.StatusTypes.ON_APPROVAL.value,
                }

    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        context['addfiles'] = AdditionalFileInlineFormset()
        context['model_id'] = ContentType.objects.get_for_model(Mission_type).id
        return context

    def post(self, request, *args, **kwargs):
        form = MissionForm(request.POST)        
        addfiles = AdditionalFileInlineFormset(request.POST,request.FILES, instance=form.instance)
        # check whether it's valid:
        if form.is_valid() :
            self.object = form.save(commit = False)
            self.object.user = request.user

            
            
            self.object.save()
            if addfiles.is_valid():
                files = addfiles.save(commit = False)
                for file in files:
                    file.request_1 = self.object
                    file.save()
                messages.success(request,'Заявка создана')
                return self.form_valid(form)
            
        messages.warning(request,'Заявка не создана')

        return self.form_invalid(form)


@method_decorator(login_required,name='dispatch')
class MissionDetailView(DetailView):
    model = Mission
    form_class = MissionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['user_is_executor'] = self.object.type.requestexecutor.filter(role=self.request.user.userprofile.role).exists() and self.object.status == Request.StatusTypes.APPROVED
        context['executor_can_edit'] = self.object.type.requestexecutor.filter(role=self.request.user.userprofile.role, can_edit=True).exists() and self.object.status == Request.StatusTypes.APPROVED
        #context['user_is_executor'] = self.object.type.requestexecutor_set.filter(role=self.request.user.userprofile.role).exists() and self.object.status == Request.StatusTypes.APPROVED

        DISALOWED_STATUS = [ Request.StatusTypes.DONE, Request.StatusTypes.CANCELED ]
        context['user_can_cancel'] = self.request.user == self.object.user and not self.object.status in DISALOWED_STATUS

        history = self.object.history.order_by('-date')
        #history = self.object.history_set.order_by('-date')
        utils.set_approval_color(history)
        context['history'] = history
        context['model_id'] = ContentType.objects.get_for_model(self.object).id
        if self.object.status == 'OA':
            approving_user = self.object.approval.filter(new_status='OA').order_by('order')[:1]
        else:
            approving_user = Approval.objects.none()
        #approving_user = self.object.approval_set.filter(new_status='OA',request__status = 'OA').order_by('order')[:1]
        if self.object.status != Request.StatusTypes.ON_REWORK and approving_user.count() > 0 :
            approving_user = approving_user.get()
            if (approving_user.user != None and approving_user.user == self.request.user) or (approving_user.role != None and approving_user.role == self.request.user.userprofile.role) :
                context['approving_user_can_edit'] = approving_user.can_edit
                approving_user = approving_user.id
            else:
                context['approving_user_can_edit'] = False
                approving_user = False
        else:
            context['approving_user_can_edit'] = False
            approving_user = False
        context['approving_user'] = approving_user


        return context

    def render_to_response(self, context):
        ALOWED_STATUS = [Request.StatusTypes.APPROVED, Request.StatusTypes.DONE]
        if ( (self.object.user == self.request.user or context['approving_user_can_edit'] ) and not self.object.status in ALOWED_STATUS) or context['executor_can_edit']  :
            return redirect('mission_update',pk=self.object.pk)
        return super(MissionDetailView,self).render_to_response(context)


@method_decorator(login_required,name='dispatch')
class MissionUpdateView(UpdateView):
    model = Mission
    form_class = MissionForm

    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)

        context['user_is_executor'] = self.object.type.requestexecutor.filter(role=self.request.user.userprofile.role).exists() and self.object.status == Request.StatusTypes.APPROVED
        context['executor_can_edit'] = self.object.type.requestexecutor.filter(role=self.request.user.userprofile.role, can_edit=True).exists() and self.object.status == Request.StatusTypes.APPROVED

        DISALOWED_STATUS = [ Request.StatusTypes.DONE, Request.StatusTypes.CANCELED ]
        context['user_can_cancel'] = self.request.user == self.object.user and not self.object.status in DISALOWED_STATUS

        if self.object.status == 'OA':
            approving_user = self.object.approval.filter(new_status='OA').order_by('order')[:1]
        else:
            approving_user = Approval.objects.none()
        #approving_user = self.object.approval_set.filter(new_status='OA',request__status = 'OA').order_by('order')[:1]
        if self.object.status != Request.StatusTypes.ON_REWORK and approving_user.count() > 0 :
            approving_user = approving_user.get()
            if (approving_user.user != None and approving_user.user == self.request.user) or (approving_user.role != None and approving_user.role == self.request.user.userprofile.role) :
                context['approving_user_can_edit'] = approving_user.can_edit
                approving_user = approving_user.id
            else:
                context['approving_user_can_edit'] = False
                approving_user = False
        else:
            context['approving_user_can_edit'] = False
            approving_user = False
        context['approving_user'] = approving_user


        history = self.object.history.order_by('-date')
        #history = self.object.history_set.order_by('-date')
        utils.set_approval_color(history)
        context['history'] = history

        modelformset = modelformset_factory(Additional_file,fields='__all__',extra=3,can_delete=True,max_num=3)
        ticket_type = ContentType.objects.get_for_model(self.object).id
        addfiles = modelformset(queryset=Additional_file.objects.filter(content_type=ticket_type,object_id=self.object.id),initial=[{
                'content_type':ticket_type,
                'object_id':self.object.id},])
        context['addfiles'] = addfiles
        context['model_id'] = ticket_type
        return context

    def post(self, request, **kwargs):
        self.object = self.get_object()

        executor_can_edit = self.object.type.requestexecutor.filter(role=self.request.user.userprofile.role, can_edit=True).exists() and self.object.status == Request.StatusTypes.APPROVED

        if self.object.status == 'OA':
            approving_user = self.object.approval.filter(new_status='OA').order_by('order')[:1]
        else:
            approving_user = Approval.objects.none()
        #approving_user = self.object.approval_set.filter(new_status='OA',request__status = 'OA').order_by('order')[:1]
        if self.object.status != Request.StatusTypes.ON_REWORK and approving_user.count() > 0 :
            approving_user = approving_user.get()
            if (approving_user.user != None and approving_user.user == self.request.user) or (approving_user.role != None and approving_user.role == self.request.user.userprofile.role) :
                user_can_edit = approving_user.can_edit
                
            else:
                user_can_edit = False
        else:
           user_can_edit  = False

        if request.user != self.object.user and user_can_edit == False and executor_can_edit== False:
            messages.warning(request,'Заявка редактируется только заявителем')
            return HttpResponseForbidden("Доступ к редактированию запрещен.")

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
                
                if request.user == self.object.user:
                    utils.reset_request_approvals(self.object)
                    periodic_tasks.send_approval_status_approved_notification(self.object)
                utils.write_history(self.object,request.user,self.object.status, comment)
                messages.success(request,'Заявка обновлена')
            
            return self.form_valid(form)
        else:
            messages.warning(request,'Не удалось обновить заявку')
            return self.form_invalid(form)

    def render_to_response(self, context):
        DISALOWED_STATUS = [Request.StatusTypes.APPROVED, Request.StatusTypes.DONE]
        if ((self.object.user != self.request.user and context['approving_user_can_edit'] == False) or self.object.status in DISALOWED_STATUS) and context['executor_can_edit'] == False:
            return redirect('mission_item',pk=self.object.pk)
        return super(MissionUpdateView,self).render_to_response(context)

@login_required
def all_requests(request):
    cur_user = request.user
    webpush = {"user": cur_user }
    return render(request,'ChainControl/all_requests.html',{'webpush':webpush})

@method_decorator(login_required,name='dispatch')
class All_requestsListView(ListView):
    template_name = "ChainControl/all_requests_list.html"
    paginate_by = 20

    def get_queryset(self):
        models_list = [Request, Mission]
        q_list = []
        cur_user = self.request.user
        approval_count = Count('approval')
        approved_count = Count('approval', filter = Q(approval__new_status = Mission.StatusTypes.APPROVED))
        #qs = super(MissionListView, self).get_queryset().annotate(approval_count = approval_count).annotate(approved_count = approved_count)

        mode = self.request.GET.get('mode','requests_for_approval')
        
        if mode == 'my_requests':
            #qs = qs.filter(user=cur_user)
            for m in models_list:
                v_n = m._meta.verbose_name
                q_list.append( m.objects.filter(user=cur_user).annotate(approval_count = approval_count).annotate(approved_count = approved_count).annotate(model_name=Value(v_n, output_field=CharField())) )

        elif mode == 'requests_to_be_done':
            #qs =qs.filter(Q(status='AP') & Q(type__requestexecutor__role=cur_user.userprofile.role)).distinct()
            for m in models_list:
                v_n = m._meta.verbose_name
                q_list.append( m.objects.filter( Q(status='AP') & Q(type__requestexecutor__role=cur_user.userprofile.role) ).distinct().annotate(approval_count = approval_count).annotate(approved_count = approved_count).annotate(model_name=Value(v_n, output_field=CharField())) )

        elif mode == 'all_requests' and cur_user.is_staff:
            #pass
            for m in models_list:
                v_n = m._meta.verbose_name
                q_list.append( m.objects.all().annotate(approval_count = approval_count).annotate(approved_count = approved_count).annotate(model_name=Value(v_n, output_field=CharField())) )
        else:
            #qs = qs.filter(Q(approval__new_status='OA', status='OA') & (Q(approval__user=cur_user) | Q(approval__role=cur_user.userprofile.role))).distinct()
            for m in models_list:
                v_n = m._meta.verbose_name
                q_list.append( m.objects.filter( Q(approval__new_status='OA', status='OA') & (Q(approval__user=cur_user) | Q(approval__role=cur_user.userprofile.role)) ).distinct().annotate(approval_count = approval_count).annotate(approved_count = approved_count).annotate(model_name=Value(v_n, output_field=CharField())) )


        ALLOWED = ('id','date','user','status')
        request_filter = MissionSearchForm(self.request.GET)
        if request_filter.is_valid():
            kwargs = dict(
                (key, value)
                for key, value in request_filter.cleaned_data.items()
                if key in ALLOWED and (value != None and value != "")
            )
            if request_filter.cleaned_data['expired']:
                kwargs['status__in'] = ['OA','AP']
                kwargs['complete_before__lte'] = datetime.now()
            for i, q in enumerate(q_list):
                q_list[i] = q.filter(**kwargs)

        for q in q_list:
            
            utils.set_approval_color(q)

        qs = sorted( list(chain(*q_list)), key=attrgetter('date') , reverse= True  )

        
        
        
        return qs
