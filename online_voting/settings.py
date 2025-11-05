import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-4x!z@#1r8$g^p7w&k2l+q9t*e3s@u0z'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# 🔹 Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'election',
    'blockchain',
    'accounts',
    'voting_app',
    'user_auth',
]

# 🔹 Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'online_voting.urls'
WSGI_APPLICATION = 'online_voting.wsgi.application'

# 🔹 Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # You can add BASE_DIR / 'templates' if needed
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

# 🔹 Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 🔹 Authentication
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/login/'

# 🔹 Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# 🔹 Static and Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'kruthi84069110@gmail.com'  # ← Your Gmail address
EMAIL_HOST_PASSWORD = 'xixwprtvdbqhzvzb'       # ← Paste your App Password here (no spaces)

TWILIO_ACCOUNT_SID = 'AC342f340cb5de3e1009e4179cdcc07b4b'
TWILIO_AUTH_TOKEN = '74368b32eb3c1141b86045ca14582d9b'
TWILIO_PHONE_NUMBER = '+91XXXXXXXXXX'