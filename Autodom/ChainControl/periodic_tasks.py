import json
from django_celery_beat.models import PeriodicTask,IntervalSchedule
from Autodom import tasks
def send_initial_notification(id):
    #schedule , created = IntervalSchedule.objects.get_or_create(
    #    every=10,
    #    period=IntervalSchedule.SECONDS,
    #)
    #PeriodicTask.objects.create(
    #interval=schedule,                  # we created this above.
    #name='Initial notification request-'+str(id),          # simply describes this periodic task.
    #task='Autodom.tasks.send_initial_notification',  # name of task.
    #args=json.dumps([id,]),
    #one_off=True,
    #)
    tasks.send_initial_notification(id,'1')