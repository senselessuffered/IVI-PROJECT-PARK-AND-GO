import os

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'parkandgo_db'),
        'USER': os.getenv('DB_USER', 'parkandgo_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'parkandgo_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
