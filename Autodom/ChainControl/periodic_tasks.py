from Autodom import tasks


def send_request_created_notification(request):
    tasks.send_request_creator_notification.delay(request.id,'1')
          
def send_approval_status_approved_notification(request):
    tasks.send_next_approval_notification.delay(request.id,'10')

def send_approval_status_on_rework_notification(request):
    tasks.send_request_creator_notification.delay(request.id,'20')

def send_request_approved_notification(request):
    tasks.send_request_creator_notification.delay(request.id,'70')
    tasks.send_executor_notification.delay(request.id,'70')

def send_request_done_notification(request):
    tasks.send_request_creator_notification.delay(request.id,'100')

def send_request_canceled_notification(request):
    tasks.send_request_creator_notification.delay(request.id,'50')

def abc():
    tasks.get_info_from_1C()