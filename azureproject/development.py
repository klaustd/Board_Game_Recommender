from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

SECRET_KEY = os.getenv('LOCAL_SECRET_KEY')

# Configure database connection for remote PostgreSQL instance.
if 'USE_REMOTE_POSTGRESQL' in os.environ:
    DB_HOST = os.environ['AZURE_POSTGRESQL_HOST']
    DB_NAME = os.environ['AZURE_POSTGRESQL_DATABASE']
    DB_USER = os.environ['AZURE_POSTGRESQL_USERNAME']
    DB_PASSWORD = os.environ['AZURE_POSTGRESQL_PASSWORD']
    # Establish connection to mail server
    MAIL_SERVER = os.environ['PROD_MAIL_SERVER']
    MAIL_PORT = os.environ['PROD_MAIL_PORT']
    MAIL_USE_TLS = os.environ['PROD_MAIL_USE_TLS']
    MAIL_USERNAME = os.environ['PROD_MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['PROD_MAIL_PASSWORD']

else:
    # Local instance settings.
    DB_HOST = os.environ['LOCAL_HOST']
    DB_NAME = os.environ['LOCAL_DATABASE']
    DB_USER = os.environ['LOCAL_USERNAME']
    DB_PORT = os.environ['LOCAL_PORT']
    DB_PASSWORD = os.environ['LOCAL_PASSWORD']
    MAIL_SERVER = os.environ['LOCAL_MAIL_SERVER']
    MAIL_PORT = os.environ['LOCAL_MAIL_PORT']
    MAIL_USE_TLS = os.environ['LOCAL_MAIL_USE_TLS']
    MAIL_USERNAME = os.environ['LOCAL_MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['LOCAL_MAIL_PASSWORD']

TIME_ZONE = 'UTC'

STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)
STATIC_URL = 'static/'