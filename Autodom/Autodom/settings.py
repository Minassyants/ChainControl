"""
Django settings for Autodom project.

Based on by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '33079540-1038-475c-84b2-bc6b03a6d221'

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True
DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True




ALLOWED_HOSTS = ["web","0.0.0.0",os.environ.get("ALLOWED_HOST","localhost")]
admin_name, admin_email = os.environ.get("ADMIN_NAME_EMAIL","Alexandr:killka1997@gmail.com").split(":")
ADMINS = [(admin_name,admin_email),]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
    'mail_admins': {
        'level': 'ERROR',
        'class': 'django.utils.log.AdminEmailHandler',
        'include_html': True,
    },
},
    }

# Application references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    # Add your apps here to enable them
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'ChainControl.apps.ChaincontrolConfig',
    'pwa_webpush',
    'tinymce',
]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'Autodom.urls'
LOGIN_URL = 'login_user'

# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Autodom.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("POSTGRES_USER",'postgres'),
        'USER': os.environ.get("POSTGRES_USER",'postgres'),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD",'password'),
        'HOST': os.environ.get("POSTGRES_HOST",'localhost'),
        'PORT': os.environ.get("POSTGRES_PORT",'8111'),
        #'ENGINE': 'django.db.backends.postgresql',
        #'NAME': 'postgres',
        #'USER': 'postgres',
        #'PASSWORD': 'password',
        #'HOST': 'localhost',
        #'PORT': 8111,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True


USE_TZ = True
DATE_FORMAT = 'Y-m-d'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "ChainControl/static"),
)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
#STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['static']))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#Celery

CELERY_BROKER_URL = os.environ.get("BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("RESULT_BACKEND")
CELERY_BEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler'


#email settings
EMAIL_HOST = os.environ.get("EMAIL_HOST") 
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = True


#PWA settings
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'serviceworker.js')
PWA_APP_NAME = 'CC'
PWA_APP_DESCRIPTION = "CC"
PWA_APP_THEME_COLOR = '#0A0302'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_DEBUG_MODE = True
PWA_APP_ICONS = [
    {
        'src': '/static/ChainControl/images/my_app_icon.png',
        'sizes': '160x160'
    }
]

PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/ChainControl/images/my_app_icon.png',
        'sizes': '160x160'
    }
]

PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/ChainControl/images/icons/splash-640x1136.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'en-US'

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "BOzJwR_LqNx6oQwX76RSPi34Oeu4yt1bpl6IZBGYQ_XAqlI6YODmVFo1ju9pwZhj--5NnrzerOwJgkGnP-BlnZ0",
    "VAPID_PRIVATE_KEY":"bwteYyg5Jf6NRaQSpR7RTcbSGZndWP632nMpMW85ZXI",
    "VAPID_ADMIN_EMAIL": "killka1997@gmail.com"
}