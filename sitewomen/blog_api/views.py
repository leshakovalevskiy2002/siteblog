from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from women.models import Women, Category
from .serializers import WomenSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly


class WomenViewSet(viewsets.ModelViewSet):
    serializer_class = WomenSerializer
    lookup_field = "slug"

    def get_queryset(self):
        subquery = Women.published.all()[:3].values_list("pk", flat=True)
        return Women.published.filter(pk__in=subquery)

    @action(methods=["get"], detail=True)
    def category(self, request, slug):
        cat = get_object_or_404(Category, where_posts__slug=slug)
        return Response({"cat": cat.name})


class WomenListPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class WomenAPIList(ListCreateAPIView):
    queryset = Women.published.all()
    serializer_class = WomenSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = WomenListPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("cat", "tags")
    search_fields = ['@title', "slug"]
    ordering_fields = ("title", "author")
    ordering = ("slug", )


class WomenAPIUpdate(RetrieveUpdateAPIView):
    queryset = Women.published.all()
    serializer_class = WomenSerializer
    permission_classes = (IsOwnerOrReadOnly, )
    authentication_classes = (TokenAuthentication, JWTAuthentication)


class WomenAPIDestroy(RetrieveDestroyAPIView):
    queryset = Women.published.all()
    serializer_class = WomenSerializer
    permission_classes = (IsAdminOrReadOnly, )
