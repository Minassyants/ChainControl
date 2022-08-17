import os
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Request, Ordering, Approval, Additional_file
from . import periodic_tasks
from . import utils
from .russian_strings import comment_create_request

@receiver(post_save, sender=Request)
def request_post_save(sender, instance, created, **kwargs):
    if created:
        utils.create_intial_approvals(instance)
        periodic_tasks.send_request_created_notification(instance)
        periodic_tasks.send_approval_status_approved_notification(instance)
        utils.write_history(instance,instance.user,instance.status,comment=comment_create_request)
    

        
@receiver(post_save, sender=Approval)
def approval_post_save(sender, instance, created, **kwargs):
    if not created and instance.new_status != Request.StatusTypes.ON_APPROVAL:
        utils.update_request_status(instance.request,instance, comment = getattr(instance, '_comment', None))

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