from rest_framework import generics, serializers

from kitsune.sumo.api import CORSMixin
from kitsune.products.models import Product, Topic


class ProductSerializer(serializers.ModelSerializer):
    platforms = serializers.SlugRelatedField(many=True, slug_field='slug')

    class Meta:
        model = Product
        fields = ('id', 'title', 'slug', 'description', 'platforms', 'visible')


class ProductList(CORSMixin, generics.ListAPIView):
    """List all documents."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = self.queryset

        is_visible = self.request.QUERY_PARAMS.get('is_visible', True)

        if is_visible is not None:
            queryset = queryset.filter(visible=is_visible)

        return queryset


class TopicSerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(slug_field='slug')
    product = serializers.SlugRelatedField(slug_field='slug')
    path = serializers.Field(source='path')

    class Meta:
        model = Topic
        fields = ('id', 'title', 'slug', 'description', 'parent', 'visible',
                  'product', 'path')


class TopicList(CORSMixin, generics.ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.filter(product__slug=self.kwargs['product'])

        is_visible = self.request.QUERY_PARAMS.get('is_visible', True)

        if is_visible is not None:
            queryset = queryset.filter(visible=is_visible)

        return queryset
