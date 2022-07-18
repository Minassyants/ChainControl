from django.apps import AppConfig


class ChaincontrolConfig(AppConfig):
    name = 'ChainControl'

    def ready(self):
        from . import signalevents