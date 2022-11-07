from Autodom import tasks
from django.contrib.contenttypes.models import ContentType

def send_request_created_notification(request):
    model_id = ContentType.objects.get_for_model(request).id
    tasks.send_request_creator_notification.delay(model_id,request.id,'1')
          
def send_approval_status_approved_notification(request):
    model_id = ContentType.objects.get_for_model(request).id
    tasks.send_next_approval_notification.delay(model_id,request.id,'10')

def send_approval_status_on_rework_notification(request):
    model_id = ContentType.objects.get_for_model(request).id
    tasks.send_request_creator_notification.delay(model_id,request.id,'20')

def send_request_approved_notification(request):
    model_id = ContentType.objects.get_for_model(request).id
    tasks.send_request_creator_notification.delay(model_id,request.id,'70')
    tasks.send_executor_notification.delay(model_id,request.id,'70')

def send_request_done_notification(request):
    model_id = ContentType.objects.get_for_model(request).id
    tasks.send_request_creator_notification.delay(model_id,request.id,'100')

def send_request_canceled_notification(request):
    model_id = ContentType.objects.get_for_model(request).id
    tasks.send_request_creator_notification.delay(model_id,request.id,'50')

#def send_request_created_notification(request):
#    tasks.send_request_creator_notification(request.id,'1')
          
#def send_approval_status_approved_notification(request):
#    tasks.send_next_approval_notification(request.id,'10')

#def send_approval_status_on_rework_notification(request):
#    tasks.send_request_creator_notification(request.id,'20')

#def send_request_approved_notification(request):
#    tasks.send_request_creator_notification(request.id,'70')
#    tasks.send_executor_notification(request.id,'70')

#def send_request_done_notification(request):
#    tasks.send_request_creator_notification(request.id,'100')

#def send_request_canceled_notification(request):
#    tasks.send_request_creator_notification(request.id,'50')