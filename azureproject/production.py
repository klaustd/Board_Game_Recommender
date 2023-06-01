import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('AZURE_SECRET_KEY')

# Configure allowed host names that can be served and trusted origins for Azure Container Apps.
ALLOWED_HOSTS = ['.azurecontainerapps.io'] if 'RUNNING_IN_PRODUCTION' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://*.azurecontainerapps.io'] if 'RUNNING_IN_PRODUCTION' in os.environ else []
DEBUG = False

# Configure database connection for Azure PostgreSQL Flexible server instance.
# AZURE_POSTGRESQL_HOST is the full URL.
# AZURE_POSTGRESQL_USERNAME is just name without @server-name.
DB_HOST = os.environ['AZURE_POSTGRESQL_HOST']
DB_NAME = os.environ['AZURE_POSTGRESQL_DATABASE']
DB_USER = os.environ['AZURE_POSTGRESQL_USERNAME']
DB_PASSWORD = os.environ['AZURE_POSTGRESQL_PASSWORD']
DB_PORT = os.environ['AZURE_POSTGRESQL_PORT']
# Establish connection to mail server
MAIL_SERVER = os.environ['AZURE_MAIL_SERVER']
MAIL_PORT = os.environ['AZURE_MAIL_PORT']
MAIL_USE_TLS = os.environ['AZURE_MAIL_USE_TLS']
MAIL_USERNAME = os.environ['AZURE_MAIL_USERNAME']
MAIL_PASSWORD = os.environ['AZURE_MAIL_PASSWORD']