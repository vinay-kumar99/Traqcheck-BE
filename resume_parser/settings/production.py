"""
Production settings.
These settings are used when DJANGO_ENV=production.
"""
from .base import *
from decouple import config
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['traqcheck-be.onrender.com']

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production!")



# Production CORS settings (strict)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = ['traqcheck-fe.vercel.app']

if not CORS_ALLOWED_ORIGINS:
    raise ValueError("CORS_ALLOWED_ORIGINS must be set in production!")


# Static files serving in production (use CDN or reverse proxy in production)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

