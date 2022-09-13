from datetime import datetime
import json
import requests as rq
from celery import shared_task
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives, mail_admins
from django.template import Template, Context
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.templatetags.static import static
from ChainControl.models import Approval, Email_templates, Request, Role, Request_type
from . import integ_1C
from Autodom import settings
from pwa_webpush import send_user_notification



@shared_task
def send_request_creator_notification(request_id,email_type):
    #MAIL BLOCK #################
    el = get_object_or_404(Request,id=request_id)
    if not el.user.email is str or len(el.user.email)<1:
        msg = f'{el.user} не указана почта'
        mail_admins("send_request_creator_notification",msg)
    else:
        mail_list = [el.user.email,]
   
        email_template = Email_templates.objects.get(email_type=email_type) #TODO: exception
    
        email_text = Template(email_template.text).render(Context({"request":el}))
        email_subject = Template(email_template.subject).render(Context({"request":el,
                                                                         "url":reverse('request_item', kwargs={"pk":str(el.id)})
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
    if len(el.user.webpush_info_set) != 0:
        user_list = [el.user,]
        notification_subject = Template(email_template.notification_subject).render(Context({"request":el}))
        notification_text = Template(email_template.notification_text).render(Context({"request":el}))
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   "url" : reverse('request_item', kwargs={"pk":str(el.id)}),
                   }
        for usr in user_list:
            send_user_notification(user=usr, payload=payload, ttl=1000)
    #END PWA BLOCK ################
    #telegram
    #if el.user.userprofile.tg_chat_id is int and len(el.user.userprofile.tg_chat_id)>1:
    if el.user.userprofile.tg_chat_id:
        tg_text = Template(email_template.tg_text).render(Context({"request":el}))
        data = {"messages": [{"chat_id": el.user.userprofile.tg_chat_id,
                                 "text":tg_text+"\n"+reverse('request_item', kwargs={"pk":str(el.id)})}]}
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'{el.user} не удалось отправить сообщение в телеграмм'
            mail_admins("send_request_creator_notification",msg)
    
    return 'done'

@shared_task
def send_next_approval_notification(request_id,email_type):
    #MAIL BLOCK #################
    el = Approval.objects.filter(request__id=request_id,new_status = 'OA')
    el = el.order_by('order')[:1]
    el = el.get()
    no_emails = []
    mail_list = []
    user_list = []
    if el.user != None:
        if not el.user.email is str or len(el.user.email)<1:
            no_emails.append(el.user)
        else:
            mail_list.append(el.user.email)
        
        user_list.append(el.user)
    else:
        usrs = User.objects.filter(userprofile__role = el.role)
        for usr in usrs:
            if not usr.email is str or len(usr.email)<1:
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
        email_template = Email_templates.objects.get(email_type=email_type) #TODO: exception
    
        email_text = Template(email_template.text).render(Context({"request":el.request}))
        email_subject = Template(email_template.subject).render(Context({"request":el.request,
                                                                         "url":reverse('request_item', kwargs={"pk":str(el.request.id)})
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
    notif_user_list = [x for x in user_list if len(x.webpush_info_set) != 0]
    if len(notif_user_list)>0:
        notification_subject = Template(email_template.notification_subject).render(Context({"request":el.request}))
        notification_text = Template(email_template.notification_text).render(Context({"request":el.request}))
        payload = {"head": notification_subject,
                    "body": notification_text,
                    "icon": static('ChainControl/images/icons/icon.ico'),
                    "url" : reverse('request_item', kwargs={"pk":str(el.request.id)}),
                    }
        for usr in notif_user_list:
            send_user_notification(user=usr, payload=payload, ttl=1000)

    #END PWA BLOCK ################
    tg_user_list = [x for x in user_list if x.userprofile.tg_chat_id]
    if len(tg_user_list)>0:
        tg_text = Template(email_template.tg_text).render(Context({"request":el.request}))
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text+"\n"+reverse('request_item', kwargs={"pk":str(el.request.id)})
                                 } for x in tg_user_list ]}
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'{el.request} не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_next_approval_notification",msg)

    return 'done'

@shared_task
def send_executor_notification(request_id,email_type):
    #MAIL BLOCK #################
    request = get_object_or_404(Request,id=request_id)
    role = request.type.executor
    no_emails = []
    mail_list = []
    user_list = []
    usrs = User.objects.filter(userprofile__role = role)
    for usr in usrs:
        if not usr.email is str or len(usr.email)<1:
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
        email_template = Email_templates.objects.get(email_type=email_type) #TODO: exception
    
        email_text = Template(email_template.text).render(Context({"request":request}))
        email_subject = Template(email_template.subject).render(Context({"request":request,
                                                                         "url":reverse('request_item', kwargs={"pk":str(request.id)})
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
    notif_user_list = [x for x in user_list if len(x.webpush_info_set) != 0]
    if len(notif_user_list)>0:
        notification_subject = Template(email_template.notification_subject).render(Context({"request":request}))
        notification_text = Template(email_template.notification_text).render(Context({"request":request}))
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   "url" : reverse('request_item', kwargs={"pk":str(request.id)}),
                   }
        for usr in user_list:
            send_user_notification(user=usr, payload=payload, ttl=1000)

    #END PWA BLOCK ################
    tg_user_list = [x for x in user_list if x.userprofile.tg_chat_id]
    if len(tg_user_list)>0:
        tg_text = Template(email_template.tg_text).render(Context({"request":request}))
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text+"\n"+reverse('request_item', kwargs={"pk":str(request.id)})
                                 } for x in tg_user_list ]}
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'{request} не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_executor_notification",msg)
    return 'done'

@shared_task
def send_daily_approval_notification():
    email_template = Email_templates.objects.get(email_type='200') #TODO: exception
    email_text = email_template.text
    email_subject = email_template.subject

    approval_roles = Role.objects.filter(approval__new_status='OA', approval__request__status='OA')
    approval_users = User.objects.filter(Q(approval__new_status='OA', approval__request__status='OA') | Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.filter(email__isnull=False).values_list('email'))
    mail_list = []
    
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_text, settings.EMAIL_HOST_USER,i))
   
    send_mass_html_mail(mail_list, fail_silently=False)

    no_emails = list(approval_users.filter(email__isnull=True))
    if len(no_emails)>0:
        msg = ""
        for i in no_emails:
            msg += f'{i} не указана почта\n'
        mail_admins("send_daily_approval_notification",msg)

    user_list = list(approval_users.filter(webpush_info__isnull=False))
    if len(user_list)>0:
        notification_subject = email_template.notification_subject
        notification_text = email_template.notification_text
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   }
        for usr in user_list:
            send_user_notification(user=usr, payload=payload, ttl=1000)

    #telegram
    tg_users = approval_users.filter(userprofile__tg_chat_id__isnull=False)
    if len(tg_users)>0:
        tg_text = email_template.tg_text
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text+"\n"+reverse('index')} for x in tg_users ]}
        
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_daily_approval_notification",msg)

    return 'done'

@shared_task
def send_deadline_passed_notificaton():
    email_template = Email_templates.objects.get(email_type='220') #TODO: exception
    email_text = email_template.text
    email_subject = email_template.subject

    approval_roles = Role.objects.filter(approval__new_status='OA',approval__request__status='OA', approval__request__complete_before__lte = datetime.now() )
    approval_users = User.objects.filter(Q(approval__new_status='OA', approval__request__status='OA', approval__request__complete_before__lte = datetime.now() ) | Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.filter(email__isnull=False).values_list('email'))
    mail_list = []
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_text, settings.EMAIL_HOST_USER,i))
   
    send_mass_html_mail(mail_list, fail_silently=False)

    no_emails = list(approval_users.filter(email__isnull=True))
    if len(no_emails)>0:
        msg = ""
        for i in no_emails:
            msg += f'{i} не указана почта\n'
        mail_admins("send_deadline_passed_notificaton",msg)

    user_list = list(approval_users.filter(webpush_info__isnull=False))
    if len(user_list)>0:
        notification_subject = email_template.notification_subject
        notification_text = email_template.notification_text
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   }
        for usr in user_list:
            send_user_notification(user=usr, payload=payload, ttl=1000)

    #telegram
    tg_users = approval_users.filter(userprofile__tg_chat_id__isnull=False)
    if len(tg_users)>0:
        tg_text = email_template.tg_text
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text+"\n"+reverse('index')} for x in tg_users ]}
        
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_deadline_passed_notificaton",msg)

    return 'done'

@shared_task
def send_daily_executor_notification():
    email_template = Email_templates.objects.get(email_type='210') #TODO: exception
    email_text = email_template.text
    email_subject = email_template.subject

    approval_roles = Request_type.objects.filter(request__status='AP').values('executor')
    approval_users = User.objects.filter(Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.filter(email__isnull=False).values_list('email'))
    mail_list = []
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_text, settings.EMAIL_HOST_USER,i))

    send_mass_html_mail(mail_list, fail_silently=False)

    no_emails = list(approval_users.filter(email__isnull=True))
    if len(no_emails)>0:
        msg = ""
        for i in no_emails:
            msg += f'{i} не указана почта\n'
        mail_admins("send_daily_executor_notification",msg)

    user_list = list(approval_users.filter(webpush_info__isnull=False))
    if len(user_list)>0:
        notification_subject = email_template.notification_subject
        notification_text = email_template.notification_text
        payload = {"head": notification_subject,
                   "body": notification_text,
                   "icon": static('ChainControl/images/icons/icon.ico'),
                   }
        for usr in user_list:
            send_user_notification(user=usr, payload=payload, ttl=1000)

    #telegram
    tg_users = approval_users.filter(userprofile__tg_chat_id__isnull=False)
    if len(tg_users)>0:
        tg_text = email_template.tg_text
        data = {"messages": [{"chat_id": x.userprofile.tg_chat_id,
                                 "text":tg_text+"\n"+reverse('index')} for x in tg_users ]}
        
        rsp = rq.post("http://tg_bot:6666/send_msg",data = json.dumps(data),headers={'Content-type':'application/json'})
        if rsp.text=="False":
            msg = f'не удалось отправить сообщение в телеграмм' #TODO добавить список пользователей с ошибками в CCTELEGRAMBOT
            mail_admins("send_daily_executor_notification",msg)

    return 'done'

@shared_task
def get_info_from_1C():
    integ_1C.getClients()
    return 'done'

@shared_task
def remove_deleted_from_1C():
    integ_1C.delClients()
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