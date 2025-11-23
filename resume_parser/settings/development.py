"""
Development settings.
These settings are used when DJANGO_ENV=development (default).
"""
from .base import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*', 'traqcheck-be.onrender.com']

# Development-specific CORS settings (more permissive)
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)

# Development logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'resume_parser': {
            'handlers': ['console'],
            'level': config('APP_LOG_LEVEL', default='DEBUG'),
            'propagate': False,
        },
    },
}


# Development email backend (console for testing)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



