from datetime import datetime
from celery import shared_task
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from django.template import Template, Context
from django.shortcuts import get_object_or_404
from django.db.models import Q, Value
from django.templatetags.static import static
from ChainControl.models import Approval, Email_templates, Request, Role
from . import integ_1C
from Autodom import settings
from pwa_webpush import send_user_notification


@shared_task
def send_initial_notification(request_id,Email_Type):
    #MAIL BLOCK #################
    el = Approval.objects.filter(request__id=request_id,new_status = 'OA')
    el = el.order_by('order')[:1]
    el = el.get()
    mail_list = [el.request.user.email,]
    user_list = [el.request.user,]
    if el.user != None:
        mail_list.append(el.user.email)
        user_list.append(el.user)
    else:
        usrs = User.objects.filter(userprofile__role = el.role)
        for usr in usrs:
            mail_list.append(usr.email)
            user_list.append(usr)

    email_template = Email_templates.objects.get(email_type=Email_Type) #TODO: exception
    
    email_text = Template(email_template.text).render(Context({"request":el.request}))
    email_subject = Template(email_template.subject).render(Context({"request":el.request}))

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
    notification_subject = Template(email_template.notification_subject).render(Context({"request":el.request}))
    notification_text = Template(email_template.notification_text).render(Context({"request":el.request}))
    payload = {"head": notification_subject,
               "body": notification_text,
               "icon": static('ChainControl/images/icons/icon.ico'),
               "url" : reverse('request_item',kwargs={'id':el.request.id}),
               }
    for usr in user_list:
        send_user_notification(user=usr, payload=payload, ttl=1000)

    #END PWA BLOCK ################
    return 'done'

#def send_status_changed_notification(id,EmailType):
#    #MAIL BLOCK #################
#    el = Approval.objects.filter(request__id=request_id,new_status = 'OA')
#    el = el.order_by('order')[:1]
#    el = el.get()
#    mail_list = [el.request.user.email,]
#    user_list = [el.request.user,]
#    if el.user != None:
#        mail_list.append(el.user.email)
#        user_list.append(el.user)
#    else:
#        usrs = User.objects.filter(userprofile__role = el.role)
#        for usr in usrs:
#            mail_list.append(usr.email)
#            user_list.append(usr)

#    email_template = Email_templates.objects.get(email_type=Email_Type) #TODO: exception
    
#    email_text = Template(email_template.text).render(Context({"request":el.request}))
#    email_subject = Template(email_template.subject).render(Context({"request":el.request}))

#    send_mail(
#    email_subject,
#    email_text,
#    settings.EMAIL_HOST_USER,
#    mail_list,
#    html_message=email_text,
#    fail_silently=False,
#)
#    #END MAIL BLOCK ###############
#    #PWA BLOCK ####################
#    notification_subject = Template(email_template.notification_subject).render(Context({"request":el.request}))
#    notification_text = Template(email_template.notification_text).render(Context({"request":el.request}))
#    payload = {"head": notification_subject,
#               "body": notification_text,

#               }
#    for usr in user_list:
#        send_user_notification(user=usr, payload=payload, ttl=1000)

#    #END PWA BLOCK ################
#    return 'done'

@shared_task
def updateclients():
    return integ_1C.getClients()

@shared_task
def send_request_creator_notification(request_id,email_type):
    #MAIL BLOCK #################
    el = get_object_or_404(Request,id=request_id)
    mail_list = [el.user.email,]
   
    email_template = Email_templates.objects.get(email_type=email_type) #TODO: exception
    
    email_text = Template(email_template.text).render(Context({"request":el}))
    email_subject = Template(email_template.subject).render(Context({"request":el}))

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
    user_list = [el.user,]
    notification_subject = Template(email_template.notification_subject).render(Context({"request":el}))
    notification_text = Template(email_template.notification_text).render(Context({"request":el}))
    payload = {"head": notification_subject,
               "body": notification_text,
               "icon": static('ChainControl/images/icons/icon.ico'),
               "url" : reverse('request_item',kwargs={'id':el.id}),
               }
    for usr in user_list:
        send_user_notification(user=usr, payload=payload, ttl=1000)

    #END PWA BLOCK ################
    return 'done'

@shared_task
def send_next_approval_notification(request_id,email_type):
    #MAIL BLOCK #################
    el = Approval.objects.filter(request__id=request_id,new_status = 'OA')
    el = el.order_by('order')[:1]
    el = el.get()
    mail_list = []
    user_list = []
    if el.user != None:
        mail_list.append(el.user.email)
        user_list.append(el.user)
    else:
        usrs = User.objects.filter(userprofile__role = el.role)
        for usr in usrs:
            mail_list.append(usr.email)
            user_list.append(usr)

    email_template = Email_templates.objects.get(email_type=email_type) #TODO: exception
    
    email_text = Template(email_template.text).render(Context({"request":el.request}))
    email_subject = Template(email_template.subject).render(Context({"request":el.request}))

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
    notification_subject = Template(email_template.notification_subject).render(Context({"request":el.request}))
    notification_text = Template(email_template.notification_text).render(Context({"request":el.request}))
    payload = {"head": notification_subject,
               "body": notification_text,
               "icon": static('ChainControl/images/icons/icon.ico'),
               "url" : reverse('request_item',kwargs={'id':el.id}),
               }
    for usr in user_list:
        send_user_notification(user=usr, payload=payload, ttl=1000)

    #END PWA BLOCK ################
    return 'done'

@shared_task
def send_executor_notification(request_id,email_type):
    #MAIL BLOCK #################
    request = get_object_or_404(Request,id=request_id)
    role = request.type.executor
    mail_list = []
    user_list = []
    usrs = User.objects.filter(userprofile__role = role)
    for usr in usrs:
        mail_list.append(usr.email)
        user_list.append(usr)

    email_template = Email_templates.objects.get(email_type=email_type) #TODO: exception
    
    email_text = Template(email_template.text).render(Context({"request":request}))
    email_subject = Template(email_template.subject).render(Context({"request":request}))

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
    notification_subject = Template(email_template.notification_subject).render(Context({"request":request}))
    notification_text = Template(email_template.notification_text).render(Context({"request":request}))
    payload = {"head": notification_subject,
               "body": notification_text,
               "icon": static('ChainControl/images/icons/icon.ico'),
               "url" : reverse('request_item',kwargs={'id':request.id}),
               }
    for usr in user_list:
        send_user_notification(user=usr, payload=payload, ttl=1000)

    #END PWA BLOCK ################
    return 'done'

@shared_task
def send_daily_approval_notification():
    email_template = Email_templates.objects.get(email_type='200') #TODO: exception
    email_text = email_template.text
    email_subject = email_template.subject

    approval_roles = Role.objects.filter(approval__new_status='OA')
    approval_users = User.objects.filter(Q(approval__new_status='OA') | Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.distinct().values_list('email',flat=True))
    mail_list = []
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_text, settings.EMAIL_HOST_USER,i))
   
    send_mass_html_mail(mail_list, fail_silently=False)


    user_list = list(approval_users.distinct())
    
    notification_subject = email_template.notification_subject
    notification_text = email_template.notification_text
    payload = {"head": notification_subject,
               "body": notification_text,
               "icon": static('ChainControl/images/icons/icon.ico'),
               }
    for usr in user_list:
        send_user_notification(user=usr, payload=payload, ttl=1000)

@shared_task
def send_deadline_passed_notificaton():
    email_template = Email_templates.objects.get(email_type='220') #TODO: exception
    email_text = email_template.text
    email_subject = email_template.subject

    approval_roles = Role.objects.filter(approval__new_status='OA', approval__request__complete_before__lte = datetime.now() )
    approval_users = User.objects.filter(Q(approval__new_status='OA', approval__request__complete_before__lte = datetime.now() ) | Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.values_list('email'))
    mail_list = []
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_text, settings.EMAIL_HOST_USER,i))
   
    send_mass_html_mail(mail_list, fail_silently=False)

    user_list = list(approval_users)
    notification_subject = email_template.notification_subject
    notification_text = email_template.notification_text
    payload = {"head": notification_subject,
               "body": notification_text,
               "icon": static('ChainControl/images/icons/icon.ico'),
               }
    for usr in user_list:
        send_user_notification(user=usr, payload=payload, ttl=1000)

@shared_task
def send_daily_executor_notification():
    email_template = Email_templates.objects.get(email_type='200') #TODO: exception
    email_text = email_template.text
    email_subject = email_template.subject

    approval_roles = Role.objects.filter(approval__new_status='OA')
    approval_users = User.objects.filter(Q(approval__new_status='OA') | Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.values_list('email'))
    mail_list = []
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_text, settings.EMAIL_HOST_USER,i))
   
    send_mass_html_mail(mail_list, fail_silently=False)

    user_list = list(approval_users)
    notification_subject = email_template.notification_subject
    notification_text = email_template.notification_text
    payload = {"head": notification_subject,
               "body": notification_text,
               "icon": static('ChainControl/images/icons/icon.ico'),
               }
    for usr in user_list:
        send_user_notification(user=usr, payload=payload, ttl=1000)

@shared_task
def send_deadline_passed_notificaton():
    email_template = Email_templates.objects.get(email_type='220') #TODO: exception
    email_text = email_template.text
    email_subject = email_template.subject

    approval_roles = Role.objects.filter(type__request__status='AP')
    approval_users = User.objects.filter(Q(userprofile__role__in = approval_roles )).distinct()
    email_list = list(approval_users.values_list('email'))
    mail_list = []
    for i in email_list:
        mail_list.append( ( email_subject, email_text, email_text, settings.EMAIL_HOST_USER,i))

    send_mass_html_mail(mail_list, fail_silently=False)

    user_list = list(approval_users)
    notification_subject = email_template.notification_subject
    notification_text = email_template.notification_text
    payload = {"head": notification_subject,
               "body": notification_text,
               "icon": static('ChainControl/images/icons/icon.ico'),
               }
    for usr in user_list:
        send_user_notification(user=usr, payload=payload, ttl=1000)


@shared_task
def get_info_from_1C():
    integ_1C.getClients()


def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, 
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)