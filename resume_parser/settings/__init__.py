"""
Django settings module.
Import the appropriate settings based on DJANGO_ENV environment variable.
"""
from decouple import config
import os

# Determine which settings to use
# Check environment variable first, then config file
ENVIRONMENT = config('DJANGO_ENV', default='development')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .development import *

