import pybars
import re
import sys
import os
import shutil
import tempfile

from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist

try:
    #django 1.8+
    from django.template.backends import BaseEngine
except ImportError:
    BaseEngine = object

try:
    import threading
except:
    import dummy_threading as threading

try:
    #python3
    from importlib.machinery import SourceFileLoader

    def sys_load_module(modname, filepath):
        loader = SourceFileLoader(modname, filepath)
        return loader.load_module()
except ImportError:
    #python2
    import imp

    def sys_load_module(modname, filepath):
        try:
            imp.acquire_lock()
            mod = imp.load_source(modname, filepath)
        except:
            raise
        finally:
            imp.release_lock()
        return mod


from .base import HandlebarsTemplate, PartialList


class TemplateInformationError(TemplateDoesNotExist):
    pass


class Handlebars(BaseEngine):

    app_dirname = 'handlebars'
    compiler = pybars.Compiler()

    def __init__(self, params):
        params = params.copy()
        options = params.pop('OPTIONS', {}).copy()
        self.precompile = options.pop('precompile', False)
        #if module_dir is set we will try to load from there
        self.module_directory = options.pop('module_directory', False)

        if self.precompile and not self.module_directory:
            raise ImproperlyConfigured(
                "A 'module_directory' is required when 'precompile' is True")

        if params:
            raise ImproperlyConfigured(
                "Unknown parameters: {}".format(", ".join(params)))

    def get_template(self, template_name, dirs=None):
        template = None
        if self.module_directory:
            template = CompiledTemplate(engine=self,
                                        template_name=template_name,
                                        module_directory=self.module_directory,
                                        template_opts={'dirs': dirs})
        if not (template and template.fn):
            if dirs:  # TODO: just assuming its a the loader
                if hasattr(dirs, 'load_template_source'):
                    source, display_name = dirs.load_template_source(template_name)
                    self._debug_template_string = source
                else:
                    pass  # TODO: handle actual dirs for Django 1.8
                template = CompiledTemplate(
                    template_string=source,
                    engine=self,
                    template_name=template_name,
                    module_directory=self.module_directory,
                    template_opts={'dirs': dirs})
        return template

    def from_string(self, template_code, **kwargs):
        if self.precompile:
            return CompiledTemplate(template_code)
        else:
            return HandlebarsTemplate(template_code, **kwargs)


class CompiledTemplate(HandlebarsTemplate):

    def __init__(self, template_string=None, origin=None, name='<Handlebars Template>',
                 partials=HandlebarsTemplate.PARTIALS, is_partial=True,
                 engine=None, template_name=None, module_directory=None,
                 template_opts={}):
        """
        This inherits from HandlebarsTemplate and then is mostly replacing the
        __init__ method.  Instead of compiling just source, we can also
        compile from template_name, module_directory.

        It's largely meant to be an internal object called by Handlbars engine
        and the legacy djangobars loaders.
        """
        self.fn = None
        self.template_opts = template_opts
        if template_string:
            #1. precompile
            if template_name and module_directory:
                if not hasattr(self.compiler, 'precompile'):
                    raise Exception("You need to upgrade pybars to support precompile.")
                CompiledTemplate.lock.acquire()
                full_code = self.compiler.precompile(template_string)
                CompiledTemplate.lock.release()
                self.write_module(template_name, module_directory, full_code)
                self.fn = self.load_module(template_name, module_directory)
            else:
                CompiledTemplate.lock.acquire()
                self.fn = self.compiler.compile(template_string)
                CompiledTemplate.lock.release()
        elif template_name and module_directory:
            #1. just try loading the module
            self.fn = self.load_module(template_name, module_directory)
        if not self.fn:
            return None  # no template
        if engine is None:
            raise Exception("engine is a required parameter for CompiledTemplate")
        self._more_init(name, partials, is_partial, engine)

    def get_template_cache_names(self, template_name, module_directory):
        filename = template_name.replace('\\', '/').replace('/', '_')
        filepath = os.path.join(module_directory, '%s.py' % filename)
        mod_name = 'djangobars._template.%s' % filename
        return (mod_name, filepath)

    def write_module(self, template_name, module_directory, source_code):
        mod_name, filepath = self.get_template_cache_names(template_name,
                                                           module_directory)
        if not os.path.exists(module_directory):
            os.makedirs(module_directory)
        (dest, name) = tempfile.mkstemp(dir=os.path.dirname(filepath))
        os.write(dest, source_code)
        os.close(dest)
        shutil.move(name, filepath)

    def load_module(self, template_name, module_directory):
        mod_name, filepath = self.get_template_cache_names(template_name,
                                                           module_directory)
        if mod_name in sys.modules:
            mod = sys.modules[mod_name]
            return mod.render
        try:
            mod = sys_load_module(mod_name, filepath)
            sys.modules[mod_name] = mod
            return mod.render
        except IOError, e:
            #no file found
            return None
