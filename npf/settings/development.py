# from .defaults import INSTALLED_APPS
from .defaults import *

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

DEBUG = True

TEMPLATE_DEBUG = True

INSTALLED_APPS = ('django_extensions', 'grappelli',) + INSTALLED_APPS

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'npfdev',
        # 'USER': 'dev',
        # 'PASSWORD': 'za3MOON2da',
    }
}

STATIC_ROOT = ''

# GRAPPELLI_ADMIN_TITLE = site.site_title

try:
    from npf.settings.local_settings import *
except ImportError:
    pass
