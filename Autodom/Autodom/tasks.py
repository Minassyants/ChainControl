from celery import shared_task
from django.core.mail import send_mail
from django.template import Template, Context
from django.template.loader import render_to_string, get_template
from ChainControl.models import Approval, Email_templates
from . import integ_1C
from Autodom import settings
@shared_task
def send_initial_notification(request_id,Email_Type):

    el = Approval.objects.filter(request__id=request_id,new_status = 'OA')
    el = el.order_by('order')[:1]
    el = el.get()
    mail_list = [el.user.email,el.request.user.email]
    email_template = Email_templates.objects.get(email_type=Email_Type) #TODO: exception
    
    email_text = Template(email_template.text).render(Context({"request":el.request}))
    email_subject = email_template.subject

    send_mail(
    email_subject,
    email_text,
    settings.EMAIL_HOST_USER,
    mail_list,
    html_message=email_text,
    fail_silently=False,
)
    return 'done'

@shared_task
def updateclients():
    return integ_1C.getClients()