from tempfile import gettempdir
from os.path import join

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS


DEBUG = True
TEMPLATE_DEBUG = DEBUG
DISABLE_CACHE_TEMPLATE = DEBUG


DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = join(gettempdir(), 'djangobaselibary_test_versionedcache.db')
TEST_DATABASE_NAME =join(gettempdir(), 'test_test_versionedcache.db')
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''


TIME_ZONE = 'Europe/Prague'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = '88b-01f^x4lh$-s5-hdccnicekg07)niir2g6)93!0#k(=mfv$'

# TODO: Fix logging
# init logger
#LOGGING_CONFIG_FILE = join(dirname(testbed.__file__), 'settings', 'logger.ini')
#if isinstance(LOGGING_CONFIG_FILE, basestring) and isfile(LOGGING_CONFIG_FILE):
#    logging.config.fileConfig(LOGGING_CONFIG_FILE)

CACHE_BACKEND = 'versionedcache.debug://127.0.0.1:11211/'

