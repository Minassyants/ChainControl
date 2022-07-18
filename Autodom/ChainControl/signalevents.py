import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django_celery_beat.models import PeriodicTask,IntervalSchedule
from .models import Request, Ordering, Approval


@receiver(post_save, sender=Request)
def request_post_save(sender, instance, created, **kwargs):
    if created:
        els = Ordering.objects.filter(request_type=instance.type).order_by('order')
        for el in els:
            Approval.objects.create(user=el.user,role=el.role,order=el.order,request=instance)

        schedule , created = IntervalSchedule.objects.get_or_create(
        every=10,
        period=IntervalSchedule.SECONDS,
    )
        PeriodicTask.objects.create(
        interval=schedule,                  # we created this above.
        name='Initial notification request-'+str(instance.id),          # simply describes this periodic task.
        task='Autodom.tasks.sendemail',  # name of task.
        args=json.dumps([instance.id,]),
        one_off=True,
    )