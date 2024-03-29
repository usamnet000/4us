"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '()xkszd8qj^t)#%bnp-p9ru%2*8r(&n33dyw&!f*&31a^z)56e'

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
    'phonenumber_field',
    'django.contrib.humanize',

    'listings.apps.ListingsConfig',
    'searches.apps.SearchesConfig',

    'social_django',
    'markdownx',
    'vote',
]

PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'YE'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.open_id.OpenIdAuth',  # for Google authentication
    'social_core.backends.google.GoogleOpenId',  # for Google authentication
    'social_core.backends.google.GoogleOAuth2',  # for Google authentication
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',  # <--
                'social_django.context_processors.login_redirect', # <--
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


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
        'NAME': 'listings.validators.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'listings.validators.MinimumLengthValidator',
    },
    {
        'NAME': 'listings.validators.CommonPasswordValidator',
    },
    {
        'NAME': 'listings.validators.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ar-AR'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static')
]


# Media Folder Settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'




EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'usamnet000@gmail.com'
SERVER_EMAIL = 'usamnet000@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'usamnet000@gmail.com'
EMAIL_HOST_PASSWORD = 'Usamnet123'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'



LOGIN_URL = '/'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = ''
LOGOUT_REDIRECT_URL = ''

SOCIAL_AUTH_FACEBOOK_KEY = '2505493123067025'  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = '8942a6136cdee2dbb4092a5aaa3c4905'  # App Secret

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '535551577887-j1pmd09l19n5g63cvg9a4lsl0his95o9.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'iwqrKSl924KWqCmd0f2V4StX'