from datetime import datetime
from asgiref.sync import async_to_sync
import json
import requests as rq
from celery import shared_task
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives, mail_admins
from django.template import Template, Context
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Value, DateField
from django.core.serializers.json import DjangoJSONEncoder
from django.templatetags.static import static
from channels.layers import get_channel_layer
from ChainControl.models import Approval, Email_templates, Request, Role, Request_type, RequestExecutor, Currency
from . import integ_1C
from Autodom import settings
from pwa_webpush import send_user_notification



channel_layer = get_channel_layer()

@shared_task
def send_request_creator_notification(request_id,email_type):
    #MAIL BLOCK #################
    el = get_object_or_404(Request,id=request_id)
    email_template = Email_templates.objects.get(email_type=email_type) #TODO: exception
    if el.user.email == "":
        msg = f'{el.user} не указана почта'
        mail_admins("send_request_creator_notification",msg)
    else:
        mail_list = [el.user.email,]
   
        
    
        email_text = Template(email_template.text).render(Context({"request":el,
                                                                   "url1":settings.BASE_URL+reverse('request_item', kwargs={"pk":str(el.id)})
                                                                   }))
        email_subject = Template(email_template.subject).render(Context({"request":el,
                                                                         
                                                                         }))

        send_mail(
        email_subject,
        email_text,
        settings.EMAIL_HOST_USER,
        mail_list,
        html_message=email_text,
        fail_silently=False,
    )
    #END MAIL BLOCK ###############
    #PWA BLOCK ####################
    notification_subject = Template(email_template.notification_subject).render(Context({"request":el}))
    notification_text = Template(email_template.notification_text).render(Context({"request":el}))
    if len(el.user.webpush_info.all()) != 0:
        user_list = [el.user,]
        
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   "url" : reverse('request_item', kwargs={"pk":str(el.id)}),
                   }
        for usr in user_list:
            try:
                send_user_notification(user=usr, payload=payload, ttl=1000)
            except:
                pass
    #END PWA BLOCK ################
    #telegram
    #if el.user.userprofile.tg_chat_id is int and len(el.user.userprofile.tg_chat_id)>1:
    tg_text = Template(email_template.tg_text).render(Context({"request":el}))
    if not el.user.userprofile.tg_chat_id is None:
        #tg_text = Template(email_template.tg_text).render(Context({"request":el}))
        data = {"messages": [{"chat_id": el.user.userprofile.tg_chat_id,
                                 "text":tg_text,
                                 "url":settings.BASE_URL+reverse('request_item', kwargs={"pk":str(el.id)}),
                                 }]}
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'{el.user} не удалось отправить сообщение в телеграмм'
            mail_admins("send_request_creator_notification",msg)
    
    #Channels
    text = {
        "subject" : notification_subject+"",
        "text" : notification_text+"",
        "url" : reverse('request_item', kwargs={"pk":str(el.id)})
        }
    async_to_sync(channel_layer.group_send)(str(el.user.id),{
        'type' : 'send_notif',
        'text' : json.dumps(text),
        })


    return 'done'

@shared_task
def send_next_approval_notification(request_id,email_type):
    #MAIL BLOCK #################
    el = Approval.objects.filter(request__id=request_id,new_status = 'OA')
    el = el.order_by('order')[:1]
    el = el.get()

    email_template = Email_templates.objects.get(email_type=email_type) #TODO: exception

    no_emails = []
    mail_list = []
    user_list = []
    if el.user != None:
        if el.user.email == "":
            no_emails.append(el.user)
        else:
            mail_list.append(el.user.email)
        
        user_list.append(el.user)
    else:
        usrs = User.objects.filter(userprofile__role = el.role)
        for usr in usrs:
            if usr.email == "":
                no_emails.append(usr)
            else:
                mail_list.append(usr.email)
            user_list.append(usr)

    if len(no_emails)>0:
        msg = ""
        for i in no_emails:
            msg += f'{i} не указана почта\n'
        mail_admins("send_next_approval_notification",msg)
    if len(mail_list)>0:
        
    
        email_text = Template(email_template.text).render(Context({"request":el.request,
                                                                   "url1":settings.BASE_URL+reverse('request_item', kwargs={"pk":str(el.request.id)})
                                                                   }))
        email_subject = Template(email_template.subject).render(Context({"request":el.request,
                                                                         
                                                                         }))

        send_mail(
        email_subject,
        email_text,
        settings.EMAIL_HOST_USER,
        mail_list,
        html_message=email_text,
        fail_silently=False,
    )
    #END MAIL BLOCK ###############
    #PWA BLOCK ####################
    notif_user_list = [x for x in user_list if len(x.webpush_info.all()) != 0]
    notification_subject = Template(email_template.notification_subject).render(Context({"request":el.request}))
    notification_text = Template(email_template.notification_text).render(Context({"request":el.request}))
    if len(notif_user_list)>0:
        
        payload = {"head": notification_subject,
                    "body": notification_text,
                    "icon": static('ChainControl/images/icons/icon.ico'),
                    "url" : reverse('request_item', kwargs={"pk":str(el.request.id)}),
                    }
        for usr in notif_user_list:
            try:
                send_user_notification(user=usr, payload=payload, ttl=1000)
            except:
                pass

    #END PWA BLOCK ################
    tg_user_list = [x for x in user_list if not x.userprofile.tg_chat_id is None]
    if len(tg_user_list)>0:
        tg_text = Template(email_template.tg_text).render(Context({"request":el.request}))
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text,
                                 "url":settings.BASE_URL+reverse('request_item', kwargs={"pk":str(el.request.id)}),
                                 } for x in tg_user_list ]}
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'{el.request} не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_next_approval_notification",msg)


    #Channels
    text = {
        "subject" : notification_subject+"",
        "text" : notification_text+"",
        "url" : reverse('request_item', kwargs={"pk":str(el.request.id)})
        }
    for usr in user_list:
        async_to_sync(channel_layer.group_send)(str(usr.id),{
            'type' : 'send_notif',
            'text' : json.dumps(text),
            })

    return 'done'

@shared_task
def send_executor_notification(request_id,email_type):
    #MAIL BLOCK #################
    request = get_object_or_404(Request,id=request_id)
    #role = request.type.executor
    no_emails = []
    mail_list = []
    user_list = []
    #usrs = User.objects.filter(userprofile__role = role)
    usrs = User.objects.filter(userprofile__role__requestexecutor__request_type= request.type)

    email_template = Email_templates.objects.get(email_type=email_type) #TODO: exception

    for usr in usrs:
        if usr.email == "":
            no_emails.append(usr)
        else:
            mail_list.append(usr.email)
        user_list.append(usr)
    if len(no_emails)>0:
        msg = ""
        for i in no_emails:
            msg += f'{i} не указана почта\n'
        mail_admins("send_executor_notification",msg)

    if len(mail_list)>0:
        
    
        email_text = Template(email_template.text).render(Context({"request":request,
                                                                   "url1":settings.BASE_URL+reverse('request_item', kwargs={"pk":str(request.id)})
                                                                   }))
        email_subject = Template(email_template.subject).render(Context({"request":request,
                                                                         
                                                                         }))

        send_mail(
        email_subject,
        email_text,
        settings.EMAIL_HOST_USER,
        mail_list,
        html_message=email_text,
        fail_silently=False,
    )
    #END MAIL BLOCK ###############
    #PWA BLOCK ####################
    notif_user_list = [x for x in user_list if len(x.webpush_info.all()) != 0]
    notification_subject = Template(email_template.notification_subject).render(Context({"request":request}))
    notification_text = Template(email_template.notification_text).render(Context({"request":request}))
    if len(notif_user_list)>0:
        notification_subject = Template(email_template.notification_subject).render(Context({"request":request}))
        notification_text = Template(email_template.notification_text).render(Context({"request":request}))
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   "url" : reverse('request_item', kwargs={"pk":str(request.id)}),
                   }
        for usr in user_list:
            try:
                send_user_notification(user=usr, payload=payload, ttl=1000)
            except:
                pass

    #END PWA BLOCK ################
    tg_user_list = [x for x in user_list if not x.userprofile.tg_chat_id is None]
    if len(tg_user_list)>0:
        tg_text = Template(email_template.tg_text).render(Context({"request":request}))
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text,
                                 "url":settings.BASE_URL+reverse('request_item', kwargs={"pk":str(request.id)}),
                                 } for x in tg_user_list ]}
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'{request} не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_executor_notification",msg)

    #Channels
    text = {
        "subject" : notification_subject+"",
        "text" : notification_text+"",
        "url" : reverse('request_item', kwargs={"pk":str(request.id)})
        }
    for usr in user_list:
        async_to_sync(channel_layer.group_send)(str(usr.id),{
            'type' : 'send_notif',
            'text' : json.dumps(text),
            })

    return 'done'

@shared_task
def send_daily_approval_notification():
    email_template = Email_templates.objects.get(email_type='200') #TODO: exception
    email_text = email_template.text
    email_html = Template(email_template.text).render(Context({"url1":settings.BASE_URL+reverse('index')}))
    email_subject = email_template.subject

    approval_roles = Role.objects.filter(approval__new_status='OA', approval__request__status='OA')
    approval_users = User.objects.filter(Q(approval__new_status='OA', approval__request__status='OA') | Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.exclude(email="").values_list('email'))
    mail_list = []
    
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_html, settings.EMAIL_HOST_USER,i))
   
    send_mass_html_mail(mail_list, fail_silently=False)

    no_emails = list(approval_users.filter(email=""))
    if len(no_emails)>0:
        msg = ""
        for i in no_emails:
            msg += f'{i} не указана почта\n'
        mail_admins("send_daily_approval_notification",msg)

    user_list = list(approval_users.filter(webpush_info__isnull=False))
    notification_subject = email_template.notification_subject
    notification_text = email_template.notification_text
    if len(user_list)>0:
        notification_subject = email_template.notification_subject
        notification_text = email_template.notification_text
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   }
        for usr in user_list:
            try:
                send_user_notification(user=usr, payload=payload, ttl=1000)
            except:
                pass

    #telegram
    tg_users = approval_users.filter(userprofile__tg_chat_id__isnull=False)
    if len(tg_users)>0:
        tg_text = email_template.tg_text
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text,
                                 "url":settings.BASE_URL+reverse('index'),
                                 } for x in tg_users ]}
        
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_daily_approval_notification",msg)


    #Channels
    text = {
        "subject" : notification_subject+"",
        "text" : notification_text+"",
        "url" : settings.BASE_URL+reverse('index'),
        }
    for usr in approval_users:
        async_to_sync(channel_layer.group_send)(str(usr.id),{
            'type' : 'send_notif',
            'text' : json.dumps(text),
            })

    return 'done'

@shared_task
def send_deadline_passed_notificaton():
    email_template = Email_templates.objects.get(email_type='220') #TODO: exception
    email_text = email_template.text
    email_html = Template(email_template.text).render(Context({"url1":settings.BASE_URL+reverse('index')}))
    email_subject = email_template.subject

    approval_roles = Role.objects.filter(approval__new_status='OA',approval__request__status='OA', approval__request__complete_before__lte = datetime.now() )
    approval_users = User.objects.filter(Q(approval__new_status='OA', approval__request__status='OA', approval__request__complete_before__lte = datetime.now() ) | Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.exclude(email="").values_list('email'))
    mail_list = []
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_html, settings.EMAIL_HOST_USER,i))
   
    send_mass_html_mail(mail_list, fail_silently=False)

    no_emails = list(approval_users.filter(email=""))
    if len(no_emails)>0:
        msg = ""
        for i in no_emails:
            msg += f'{i} не указана почта\n'
        mail_admins("send_deadline_passed_notificaton",msg)

    user_list = list(approval_users.filter(webpush_info__isnull=False))
    notification_subject = email_template.notification_subject
    notification_text = email_template.notification_text
    if len(user_list)>0:
        
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   }
        for usr in user_list:
            try:
                send_user_notification(user=usr, payload=payload, ttl=1000)
            except:
                pass

    #telegram
    tg_users = approval_users.filter(userprofile__tg_chat_id__isnull=False)
    if len(tg_users)>0:
        tg_text = email_template.tg_text
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text,
                                 "url":settings.BASE_URL+reverse('index'),
                                 } for x in tg_users ]}
        
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_deadline_passed_notificaton",msg)


    #Channels
    text = {
        "subject" : notification_subject+"",
        "text" : notification_text+"",
        "url" : settings.BASE_URL+reverse('index'),
        }
    for usr in approval_users:
        async_to_sync(channel_layer.group_send)(str(usr.id),{
            'type' : 'send_notif',
            'text' : json.dumps(text),
            })

    return 'done'

@shared_task
def send_daily_executor_notification():
    email_template = Email_templates.objects.get(email_type='210') #TODO: exception
    email_text = email_template.text
    email_html = Template(email_template.text).render(Context({"url1":settings.BASE_URL+reverse('index')}))
    email_subject = email_template.subject

    #approval_roles = Request_type.objects.filter(request__status='AP').values('executor')
    approval_roles = RequestExecutor.objects.filter(request_type__request__status='AP').values('role')
    approval_users = User.objects.filter(Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.exclude(email="").values_list('email'))
    mail_list = []
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_html, settings.EMAIL_HOST_USER,i))

    send_mass_html_mail(mail_list, fail_silently=False)

    no_emails = list(approval_users.filter(email=""))
    if len(no_emails)>0:
        msg = ""
        for i in no_emails:
            msg += f'{i} не указана почта\n'
        mail_admins("send_daily_executor_notification",msg)

    user_list = list(approval_users.filter(webpush_info__isnull=False))
    notification_subject = email_template.notification_subject
    notification_text = email_template.notification_text
    if len(user_list)>0:
        
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   }
        for usr in user_list:
            try:
                send_user_notification(user=usr, payload=payload, ttl=1000)
            except:
                pass

    #telegram
    tg_users = approval_users.filter(userprofile__tg_chat_id__isnull=False)
    if len(tg_users)>0:
        tg_text = email_template.tg_text
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text,
                                 "url":settings.BASE_URL+reverse('index'),
                                 } for x in tg_users ]}
        
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_daily_executor_notification",msg)

    #Channels
    text = {
        "subject" : notification_subject+"",
        "text" : notification_text+"",
        "url" : settings.BASE_URL+reverse('index'),
        }
    for usr in approval_users:
        async_to_sync(channel_layer.group_send)(str(usr.id),{
            'type' : 'send_notif',
            'text' : json.dumps(text),
            })

    return 'done'

@shared_task
def get_info_from_1C():
    integ_1C.getClients()
    return 'done'

@shared_task
def remove_deleted_from_1C():
    integ_1C.delClients()
    return 'done'

@shared_task
def get_individuals():
    integ_1C.getIndividuals()
    return 'done'

@shared_task
def send_accounts_payable():
    accounts_payable = list(Currency.objects.annotate(amount=Sum('request__sum', filter = Q(request__status='AP',)),date=Value(datetime.now(),DateField())).filter(amount__gt=0).values('date','code_str','amount'))
    jp = json.dumps(accounts_payable,cls= DjangoJSONEncoder)
    rq.post("https://hino-aa.minassyants.kz/api/update_accounts_payable",json=jp)
    return 'done'

def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, 
                        connection=None):
    
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)