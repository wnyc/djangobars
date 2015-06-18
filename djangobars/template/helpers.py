from django.template import defaultfilters
from django.template import defaulttags
from django.core.urlresolvers import reverse


def _url(context, url_name, *args, **kwargs):
    return reverse(url_name, args=args, kwargs=kwargs)

_djangobars_ = {
    'helpers': {
        'url': _url
    }
}

def register_tag(name, filter_func):
    _djangobars_['helpers'][name] = filter_func
