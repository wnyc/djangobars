from django.template.loaders.filesystem import Loader as CoreLoader
from django.template.loaders.cached import Loader as DjangoCachedLoader
from djangobars import settings
from djangobars.template.loader import BaseHandlebarsLoader

class Loader(BaseHandlebarsLoader, CoreLoader):

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Returns the absolute paths to "template_name", when appended to each
        directory in "template_dirs". Any paths that don't lie inside one of the
        template dirs are excluded from the result set, for security reasons.
        """
        dirs = getattr(settings, 'HANDLEBARS_DIRS', None)
        return super(Loader, self).get_template_sources(template_name,
                                                        template_dirs=dirs)


class CachedLoader(DjangoCachedLoader, Loader):

    def __init__(self):
        self.template_cache = {}
        self.find_template_cache = {}
        self._loaders = [Loader()]

    @property
    def loaders(self):
        return self._loaders
