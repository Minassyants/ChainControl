import os

from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Autodom.settings')

app = Celery('Autodom')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

#@app.on_after_configure.connect
#def setup_periodic_tasks(sender, **kwargs):
#    # Calls test('hello') every 10 seconds.
#    sender.add_periodic_task(10.0, add(10,13), name='add every 10')

# Load task modules from all registered Django apps.
@app.on_after_finalize.connect
def disc_tasks(sender,**kwargs):
    from . import tasks
    sender.autodiscover_tasks()
