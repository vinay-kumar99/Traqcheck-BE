"""
App configuration for persistence layer.
"""
from django.apps import AppConfig


class PersistenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infrastructure.persistence'
    label = 'persistence'

