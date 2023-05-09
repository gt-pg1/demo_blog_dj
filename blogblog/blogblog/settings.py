"""
Django settings for blogblog project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4p&5*j_7p&rv_x2+!n0^u@z^-u0%y=7%fr@w5fjye*(c*z1nfg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
    'debug_toolbar',
    'tinymce',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'blogblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.auth',
            ],
        },
    },
]

WSGI_APPLICATION = 'blogblog.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'demo_blog_dj',
        'USER': 'dev',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = '/login'

TINYMCE_DEFAULT_CONFIG = {
    'plugins': 'paste, emoticons, lists, searchreplace, table, hr, link, code, wordcount',
    'paste_as_text': True,
    'height': 400,
    'skin': 'oxide-dark',
    'menubar': False,
    'toolbar': [
        {
            'name': 'history', 'items': ['undo', 'redo']
        },
        {
            'name': 'style', 'items': ['styleselect', 'h2', 'h3', 'bold', 'italic', 'blockquote', 'hr']
        },
        {
            'name': 'alignment', 'items': ['alignleft', 'aligncenter', 'alignright', 'alignjustify']
        },
        {
            'name': 'indents', 'items': ['outdent', 'indent']
        },
        {
            'name': 'link', 'items': ['link']
        },
        {
            'name': 'lists', 'items': ['numlist', 'bullist']
        },
        {
            'name': 'table', 'items': ['table']
        },
        {
            'name': 'additional', 'items': ['searchreplace', 'emoticons', 'wordcount']
        }
    ],
    # 'toolbar_drawer' and 'toolbar_mode' add an extra menu that will hide menu items that won't fit
    # toolbar_drawer is actual for v5.1, toolbar_mode will actual for v5.2 and higher
    'toolbar_drawer': 'floating',
    'toolbar_mode': 'floating',
    # Simplifying the menu for adding links
    'link_title': False,
    'link_url': True,
    'link_text': True,
    'target_list': False,
    'default_link_target': '_blank',
    'setup': open(os.path.join(BASE_DIR, 'blog', 'static', 'blog', 'js', 'tinymce-setup.js')).read()

}
