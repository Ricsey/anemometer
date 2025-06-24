from datetime import timedelta
from django.db import transaction
from django.db.models import Avg, OuterRef, Subquery
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .paginations import DefaultPagination
from .throttling import WindReadingSubmitThrottle
from .serializers import AnemometerSerializer, AnemometerDetailSerializer, WindReadingSerializer, CreateWindReadingSerializer, CreateNestedWindReadingSerializer, TagSerializer
from .models import Anemometer, Tag, WindReading

class AnemometerViewSet(ModelViewSet):
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tags']
    throttle_classes = [WindReadingSubmitThrottle]

    def get_queryset(self):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        daily_avg_subquery = WindReading.objects.filter(
            anemometer=OuterRef('pk'),
            timestamp__date=today
        ).values('anemometer').annotate(avg=Avg('speed')).values('avg')

        weekly_avg_subquery = WindReading.objects.filter(
            anemometer=OuterRef('pk'),
            timestamp__date__gte=start_of_week
        ).values('anemometer').annotate(avg=Avg('speed')).values('avg')

        qs = Anemometer.objects.all().prefetch_related('tags')
        qs = qs.annotate(
            daily_avg=Subquery(daily_avg_subquery),
            weekly_avg=Subquery(weekly_avg_subquery)
        )
        return qs

    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return AnemometerDetailSerializer
        return AnemometerSerializer


class NestedWindReadingViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['anemometer__tags']
    def get_queryset(self):
        anemometer_id = self.kwargs['anemometer_pk']
        return WindReading.objects.filter(anemometer_id = anemometer_id)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return CreateNestedWindReadingSerializer
        return WindReadingSerializer
    
    def get_serializer_context(self):
        return {
            'anemometer_id': self.kwargs['anemometer_pk']
        }

class NestedBulkReadingViewSet(ModelViewSet):
    serializer_class = CreateNestedWindReadingSerializer
    http_method_names = ['post']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WindReadingViewSet(ModelViewSet):
    queryset = WindReading.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['anemometer__tags']

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return CreateWindReadingSerializer
        return WindReadingSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
