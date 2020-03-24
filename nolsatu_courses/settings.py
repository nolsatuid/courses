"""
Django settings for nolsatu_courses project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SETTINGS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(SETTINGS_DIR)
PROJECT_NAME = os.path.basename(PROJECT_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n-@n7d!%na!&^cd4^%al(z4%2vq0umr+fy_m6gmc(0_4uxbuwx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

HOST = 'https://course.nolsatu.id'
NOLSATU_HOST = 'https://www.nolsatu.id'

LOGIN_URL = f"{NOLSATU_HOST}/accounts/login/"
LOGOUT_URL = f"{NOLSATU_HOST}/accounts/logout/"
LOGOUT_REDIRECT_URL = HOST

NOLSATU_PROFILE_URL = f'{NOLSATU_HOST}/profile'
NOLSATU_PROFILE_PAGE_URL = f'{NOLSATU_HOST}/accounts/profile/'
LOGIN_URL = f"{NOLSATU_HOST}/accounts/login/?navbar=hidden"
LOGOUT_URL = f"{NOLSATU_HOST}/accounts/logout/"

IMG_LOGO = ""
BRAND = "NolDua"
COLOR_THEME = "warning"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'nolsatu_courses.apps.courses',
    'nolsatu_courses.apps.upload_files',
    'nolsatu_courses.apps.accounts',

    # other apps
    'django_extensions',
    'taggit',
    'ckeditor',
    'ckeditor_uploader',
    'widget_tweaks',
    'rest_framework',
    'drf_yasg'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'nolsatu_courses.apps.middleware.NolSatuAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_ENGINE = 'redis_sessions.session'

ROOT_URLCONF = 'nolsatu_courses.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'nolsatu_courses.apps.context_processors.nolsatu_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'nolsatu_courses.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'id'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static_files'),
)
STATIC_ROOT = os.path.join(SETTINGS_DIR, 'static')

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'width': '100%',
    },
    'basic_ckeditor': {
        'toolbar': 'Basic',
        'width': '100%',
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': []
}

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_DOMAIN = '.nolsatu.id'

SERVER_KEY = "serverToServerAuthKeyKeepItVerySecret"

# API Docs
API_DOC_USERNAME = "nolsatu"
API_DOC_PASSWORD = "nolsatumantap"

try:
    from .local_settings import *
except ImportError:
    pass