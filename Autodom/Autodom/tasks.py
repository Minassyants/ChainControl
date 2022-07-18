from celery import shared_task
from django.core.mail import send_mail
from ChainControl.models import Approval
from . import integ_1C

@shared_task
def add(x, y):
    return x + y

@shared_task
def sendemail(request_id):

    els = Approval.objects.filter(request__id=request_id)
    mail_list = []
    for el in els:
        mail_list.append(el.user.email)

    send_mail(
    'Subject here',
    'Here is the message.',
    'info@minassyants.kz',
    mail_list,
    fail_silently=False,
)
    return 'done'

@shared_task
def updateclients():
    return integ_1C.getClients()