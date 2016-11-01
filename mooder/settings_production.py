from mooder.settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql') ,
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django_mailgun.MailgunBackend')
if EMAIL_BACKEND=='django_mailgun.MailgunBackend':
    MAILGUN_ACCESS_KEY = os.environ.get('MAILGUN_ACCESS_KEY')
    MAILGUN_SERVER_NAME = os.environ.get('MAILGUN_SERVER_NAME')

if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = os.environ.get('EMAIL_PORT')
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', None)
    if EMAIL_USE_SSL and EMAIL_USE_SSL.lower() == 'false':
        EMAIL_USE_SSL = None
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', None)
    if EMAIL_USE_TLS and EMAIL_USE_TLS.lower() == 'false':
        EMAIL_USE_TLS = None

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'mooder', 'static_cdn')

MEDIA_URL = '/media/'
MEDIA_ROOT = '/data'