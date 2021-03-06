from django.conf import settings
from rest_framework.exceptions import APIException
from rest_framework import fields
from django import forms
from tower import ugettext as _

from kitsune.sumo.utils import uselocale
from kitsune.sumo.urlresolvers import get_best_language


class CORSMixin(object):
    """Sets headers on a request to allow cross-origin access to the api."""
    def finalize_response(self, request, response, *args, **kwargs):
        response = (super(CORSMixin, self)
                    .finalize_response(request, response, *args, **kwargs))
        response['Access-Control-Allow-Origin'] = '*'
        return response


class GenericAPIException(APIException):
    """Generic Exception, since DRF doesn't provide one.

    DRF allows views to throw subclasses of APIException to cause non-200
    status codes to be sent back to API consumers. These subclasses are expected
    to have a ``status_code`` and ``detail`` property.

    DRF doesn't give a generic way to make an object with these properties.
    Instead you are expected to make many specific subclasses and make instances
    of those. That seemed lame, so this class creates instances instead of lots
    of subclasses.
    """
    def __init__(self, status_code, detail, **kwargs):
        self.status_code = status_code
        self.detail = detail
        for key, val in kwargs.items():
            setattr(self, key, val)


class LocaleNegotiationMixin(object):
    """A mixin for CBV to select a locale based on Accept-Language headers."""

    def get_locale(self):
        accept_language = self.request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        lang = get_best_language(accept_language)
        return lang or settings.WIKI_DEFAULT_LANGUAGE

    def get_serializer_context(self):
        context = super(LocaleNegotiationMixin, self).get_serializer_context()
        context['locale'] = self.get_locale()
        return context


class LocalizedCharField(fields.CharField):
    """
    This is a field for DRF that localizes itself based on the current locale.

    There should be a locale field on the serialiation context. If the view
    that uses this serializer subclasses LocaleNegotiationMixin, the context
    will get a locale field automatically.

    A serializer can use this field like this:

        class FooSerializer(serializers.ModelSerializer):
            title = LocalizedCharField(source='title',
                                       l10n_context='DB: bar.Foo.title')
            class Meta:
                model = Foo
                fields = ('id', 'title')

    :args l10n_context: Set the localization context, mainly for fields that
        come from the DB.
    """
    type_name = 'LocalizedCharField'
    type_label = 'string'
    form_field_class = forms.CharField
    read_only = True

    def __init__(self, *args, **kwargs):
        self.l10n_context = kwargs.pop('l10n_context', None)
        super(LocalizedCharField, self).__init__(*args, **kwargs)

    def to_native(self, value):
        value = super(LocalizedCharField, self).from_native(value)
        locale = self.context.get('locale')

        if locale is None:
            return value
        with uselocale(locale):
            return _(value, self.l10n_context)
