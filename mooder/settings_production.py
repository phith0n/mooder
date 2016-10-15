from mooder.settings import *

SECRET_KEY = 'tcydk1&&g1iej0#pchikrlt)5uw@t^t&4#=a1f9@^5waz_9=f&'
DEBUG = False
ALLOWED_HOSTS = ['*']
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mooder',
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = os.environ.get('MAILGUN_ACCESS_KEY')
MAILGUN_SERVER_NAME = os.environ.get('MAILGUN_SERVER_NAME')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'mooder', 'static_cdn')

MEDIA_URL = '/media/'
MEDIA_ROOT = '/data'