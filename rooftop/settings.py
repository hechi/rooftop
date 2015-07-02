"""
Django settings for rooftop project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ldap
from django_auth_ldap.config import LDAPSearch, NestedActiveDirectoryGroupType, GroupOfNamesType
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open(os.path.join(BASE_DIR,'secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (
        os.path.join(BASE_DIR, 'rooftop/templates'),
)

ALLOWED_HOSTS = ["localhost","127.0.0.1"]

### LDAP STUFF

# Binding and connection options
AUTH_LDAP_SERVER_URI = "ldap://192.168.56.101:389"
AUTH_LDAP_BIND_DN = "cn=admin,dc=example,dc=de"
AUTH_LDAP_BASE_USER_DN = "ou=users,dc=example,dc=de"
AUTH_LDAP_BASE_GROUP_DN = "ou=groups,dc=example,dc=de"
AUTH_LDAP_BIND_PASSWORD = "root"

# SECURITY WARNING: keep the secret key used in production secret!
with open(os.path.join(BASE_DIR,'ldap_passwd.txt')) as f:
    AUTH_LDAP_BIND_PASSWORD = f.read().strip()

AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 1,
    ldap.OPT_REFERRALS: 1,
}

# User and group search objects and types
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=de",
    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=example,dc=de",
    ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)")
#AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr='cn')

# Cache settings
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 5

# What to do once the user is authenticated
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "cn",
    "last_name": "sn",
    "displayname" : "displayName",
    "email": "mail",
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
}

AUTH_LDAP_PROFILE_FLAGS_BY_GROUP = {
}
AUTH_LDAP_FIND_GROUP_PERMS = True

# The backends needed to make this work.
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend'
)
### /LDAP STUFF

# page after successful login
LOGIN_URL = '/'

LOGIN_REDIRECT_URL = '/start/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rooftop.urls'

WSGI_APPLICATION = 'rooftop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR,'rooftop/static'),
)

