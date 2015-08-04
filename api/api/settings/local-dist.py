SECRET_KEY = 'My Secret Key'

DEBUG = True

DOMAIN = 'http://localhost:8000'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'scrapi',
        # 'USER': 'name',
        # 'PASSWORD': 'password',
        # 'HOST': '127.0.0.1',
        # 'PORT': '5432'
    }
}

STATIC_URL = '/static/'


CORS_ORIGIN_WHITELIST = (
    'localhost:5000',
    'osf.io',
    'staging.osf.io'
)
