from django.conf import settings

HANDLEBARS_LOADERS = getattr(settings, 'HANDLEBARS_LOADERS', (
    'djangobars.template.loaders.filesystem.Loader',
    'djangobars.template.loaders.app_directories.Loader',
))

# If not present, HANDLEBARS_DIRS will mimic TEMPLATE_DIRS
if hasattr(settings, 'HANDLEBARS_DIRS'):
    HANDLEBARS_DIRS = settings.HANDLEBARS_DIRS

# If not present, HANDLEBARS_APP_DIRNAME will be 'templates'
if hasattr(settings, 'HANDLEBARS_APP_DIRNAMES'):
    HANDLEBARS_APP_DIRNAMES = settings.HANDLEBARS_APP_DIRNAMES

if hasattr(settings, 'INSTALLED_APPS'):
    INSTALLED_APPS = settings.INSTALLED_APPS

# This is a backwards-compatible way to get OPTIONS previous to Django 1.8
if hasattr(settings, 'HANDLEBARS_OPTS'):
    HANDLEBARS_OPTS = settings.HANDLEBARS_OPTS
