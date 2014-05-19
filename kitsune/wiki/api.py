from django.shortcuts import get_object_or_404

from rest_framework import generics, serializers, status
from rest_framework.exceptions import APIException

from kitsune.wiki.models import Document


class DocumentShortSerializer(serializers.ModelSerializer):
    products = serializers.SlugRelatedField(many=True, slug_field='slug')
    topics = serializers.SlugRelatedField(many=True, slug_field='slug')

    class Meta:
        model = Document
        fields = ('id', 'title', 'slug', 'locale', 'products', 'topics')


class DocumentDetailSerializer(DocumentShortSerializer):
    class Meta:
        model = Document
        fields = ('id', 'title', 'slug', 'locale', 'products', 'topics',
                  'html')


class CORSMixin(object):
    def finalize_response(self, request, response, *args, **kwargs):
        response = (super(CORSMixin, self)
                    .finalize_response(request, response, *args, **kwargs))
        response['Access-Control-Allow-Origin'] = '*'
        return response


class GenericAPIException(APIException):
    def __init__(self, status_code, detail, **kwargs):
        self.status_code = status_code
        self.detail = detail
        for key, val in kwargs.items():
            setattr(self, key, val)


class DocumentList(CORSMixin, generics.ListAPIView):
    """List all documents."""
    queryset = Document.objects.all()
    serializer_class = DocumentShortSerializer
    paginate_by = 10

    def get_queryset(self):
        queryset = self.queryset

        locale = self.request.QUERY_PARAMS.get('locale')
        product = self.request.QUERY_PARAMS.get('product')
        topic = self.request.QUERY_PARAMS.get('topic')
        is_template = self.request.QUERY_PARAMS.get('is_template', False)
        is_archived = self.request.QUERY_PARAMS.get('is_archived', False)

        if locale is not None:
            queryset = queryset.filter(locale=locale)

        if product is not None:
            queryset = queryset.filter(products__slug=product)
            if topic is not None:
                queryset = queryset.filter(topics__slug=topic,
                                           topics__product__slug=product)
        elif topic is not None:
            raise GenericAPIException(status.HTTP_400_BAD_REQUEST,
                                      'topic requires product')

        if is_template is not None:
            queryset = queryset.filter(is_template=is_template)

        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived)

        return queryset


class DocumentDetail(CORSMixin, generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentDetailSerializer

    def get_object(self):
        queryset = self.get_queryset()
        filter = {
            'locale': 'en-US',
        }
        filter.update(self.kwargs)

        obj = get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj
