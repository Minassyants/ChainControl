from datetime import datetime
from django.db.models import CharField, Value
from django.contrib.auth.models import User
from .models import  Approval,Request,Ordering,History
from . import russian_strings, periodic_tasks
colors = {
    'OP':'text-primary',
    'OA':'text-primary',
    'AP':'text-success',
    'OR':'text-warning',
    'CA':'text-danger',
    'DO':'text-success',
    }


def reset_request_approvals(instance):
    for el in instance.approval_set.all():
        el.new_status = Request.StatusTypes.ON_APPROVAL
        el.save()

def update_request_status(instance,approval,comment = None):
    total_count = instance.approval_set.count()
    approved_count = instance.approval_set.filter(new_status = Request.StatusTypes.APPROVED).count()
    rework_count = instance.approval_set.filter(new_status = Request.StatusTypes.ON_REWORK).count()
    cancel_count = instance.approval_set.filter(new_status = Request.StatusTypes.CANCELED).count()
    if approved_count == total_count:
        instance.status = Request.StatusTypes.APPROVED
        instance.save()
        periodic_tasks.send_request_approved_notification(instance)
        write_history(request = instance,user = approval.user, status = instance.status, comment= comment if comment else russian_strings.comment_request_approved)
        return
        
    if rework_count > 0:
        instance.status = Request.StatusTypes.ON_REWORK
        periodic_tasks.send_approval_status_on_rework_notification(instance)
        instance.save()
        instance.approval_set.all().update(new_status=Request.StatusTypes.ON_APPROVAL)
        write_history(request = instance,user = approval.user, status = instance.status, comment= comment if comment else russian_strings.comment_request_on_rework)
        return

    if cancel_count > 0:
        instance.status = Request.StatusTypes.CANCELED
        periodic_tasks.send_request_canceled_notification(instance)
        instance.save()
        instance.approval_set.all().update(new_status=Request.StatusTypes.ON_APPROVAL)
        write_history(request = instance,user = approval.user, status = instance.status, comment= comment if comment else russian_strings.comment_request_canceled)
        return
        
    periodic_tasks.send_approval_status_approved_notification(instance)
    write_history(request = instance,user = approval.user, status = approval.new_status, comment= comment if comment else russian_strings.comment_new_status)
    


    
def write_history(request: Request,user : User , status : Request.StatusTypes, comment : str):
    History.objects.create(request=request,user=user,status=status,comment=comment, date = datetime.now())


def get_ordering_number(role,request_type):
    try:
        role_order = request_type.ordering_set.get(role=role).order
        return role_order
    except:
        return -1

def create_intial_approvals(instance):
    #els = Ordering.objects.filter(request_type=instance.type).order_by('order').exclude(user=instance.user).exclude(role=instance.user.userprofile.role)
    els = Ordering.objects.filter(request_type=instance.type).order_by('order').exclude(order__lte=get_ordering_number(instance.user.userprofile.role,instance.type))
    if els.count() > 0:
        for el in els:
            Approval.objects.create(user=el.user,role=el.role,order=el.order,request=instance)

def set_approval_color(els):
    els.annotate(color=Value('xxx', output_field=CharField()))
    if els.model == Approval:
        for el in els:
            el.color = colors[el.new_status]
    else:
        for el in els:
            el.color = colors[el.status]



    
