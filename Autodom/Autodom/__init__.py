"""
Package for Autodom.
"""
import os
from .celery_init import app as celery_app

__all__ = ('celery_app',)


