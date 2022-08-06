from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Request, Ordering, Approval
from . import periodic_tasks

@receiver(post_save, sender=Request)
def request_post_save(sender, instance, created, **kwargs):
    if created:
        els = Ordering.objects.filter(request_type=instance.type).order_by('order').exclude(user=instance.user,role=instance.user.userprofile.role)
        for el in els:
            Approval.objects.create(user=el.user,role=el.role,order=el.order,request=instance)

        periodic_tasks.send_initial_notification(instance.id)
        