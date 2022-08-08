import os
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Request, Ordering, Approval, Additional_file
from . import periodic_tasks

@receiver(post_save, sender=Request)
def request_post_save(sender, instance, created, **kwargs):
    if created:
        els = Ordering.objects.filter(request_type=instance.type).order_by('order').exclude(user=instance.user,role=instance.user.userprofile.role)
        for el in els:
            Approval.objects.create(user=el.user,role=el.role,order=el.order,request=instance)

        periodic_tasks.send_initial_notification(instance.id)
        

@receiver(post_delete, sender=Additional_file)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

@receiver(pre_save, sender=Additional_file)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Additional_file.objects.get(pk=instance.pk).file
    except Additional_file.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)