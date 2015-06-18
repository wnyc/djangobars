djangobars
==========

An extension to allow Django to use Handlebars templates through the pybars port
of Handlebars.js

Because don't we all want to use the same templates on the client that we do on
the server?

.. image:: https://travis-ci.org/mjumbewu/djangobars.png?branch=master
  :target: https://travis-ci.org/mjumbewu/djangobars

**NOTE: This project is very early-stage.  Try it out, leave feedback and wishes
in the issues.  And pull-requests welcome!**

Installation
------------

1. Install ``djangobars``::

    pip install djangobars

2. Add ``'djangobars'`` to your installed applications.

3. Add a ``HANDLEBARS_LOADERS`` value to your settings module. You will probably
   want::

       HANDLEBARS_LOADERS = (
           'djangobars.template.loaders.filesystem.Loader',
           'djangobars.template.loaders.app_directories.Loader',
       )

4. *(optional)* Add a ``HANDLEBARS_DIRS`` and/or ``HANDLEBARS_APP_DIRNAMES``
   value to your setting module. By
   default, djangobars will search in your ``TEMPLATE_DIRS`` folder, but you can
   use the ``HANDLEBARS_DIRS`` value to override this behavior. For example, if
   you want to use both Django templates and Handlebars templates, you may want
   to keep the two in separate directories.


Usage
-----

Use pretty much just as you would Django's own built-in templates.  Instead of::

    from django.shortcuts import render

    def my_view(request):
        # View code here...
        return render(request, 'myapp/index.html', {"foo": "bar"},
            content_type="application/xhtml+xml")

do this::

    from djangobars.shortcuts import render

    def my_view(request):
        # View code here...
        return render(request, 'myapp/handlebar_index.html', {"foo": "bar"},
            content_type="application/xhtml+xml")

And instead of::

    from django.views.generic import TemplateView

    class MyView (TemplateView):
        template_name = 'myapp/index.html'

do this::

    from django.views.generic import TemplateView
    from djangobars.response import HandlebarsResponse

    class MyView (TemplateView):
        template_name = 'myapp/handlebar_index.html'
        response_class = HandlebarsResponse

Template Tags
-------------

You can also include Handlebars templates with a Django template tag::

    {% load djangobars %}

    {% include_handlebars "handlebars_template_name.html" %}

The current template context will be carried over into the Handlebars template.


Helpers
-------

Included in Djangobars is a `url` helper, so you can do::

    {{url some-url-pattern id}}

and it will be run through Django's resolve() method.

You can also register your own helpers with:

    from djangobars.template.helpers import register_tag

    def some_foo_tag(context, *args):
        return 'foo'

    register_tag('foo', some_foo_tag)

which will then allow you to use `{{foo ...}}` in your templates.
