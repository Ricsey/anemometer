from django.utils import timezone as django_timezone
from datetime import timedelta, datetime, timezone
from rest_framework import serializers
from django.db.models import Avg

from .models import Anemometer, WindReading, Tag

ALLOWED_MIN_WINDSPEED = 0
ALLOWED_MAX_WINDSPEED = 300

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
        ]


class SimpleTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']

class AnemometerSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Anemometer
        fields = [
            "id",
            "name",
            "tags", 
        ]

class AnemometerDetailSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    tags = SimpleTagSerializer(many=True)
    last_five_readings = serializers.SerializerMethodField()
    daily_avg = serializers.FloatField(read_only=True)
    weekly_avg = serializers.FloatField(read_only=True)


    def get_last_five_readings(self, obj):
        last_five_readings = obj.wind_readings.all()[:5]
        return WindReadingSerializer(last_five_readings, many=True).data

    class Meta:
        model = Anemometer
        fields = [
            "id",
            "name",
            "tags", 
            "last_five_readings",
            "daily_avg",
            "weekly_avg",
        ]


class WindReadingSerializer(serializers.ModelSerializer):
    anemometer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WindReading
        fields = [
            "id",
            "anemometer",
            "speed",
            "timestamp",
        ]

class BulkWindreadingSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        anemometer_id = self.context['anemometer_id']
        anemometer = Anemometer.objects.get(id=anemometer_id)

        wind_readings = [
            WindReading(
                anemometer=anemometer,
                speed=item['speed'],
                timestamp=item.get('timestamp', timezone.now())
            )
            for item in validated_data
        ]
        return WindReading.objects.bulk_create(wind_readings)


class CreateWindReadingSerializer(serializers.ModelSerializer):
    anemometer_id = serializers.UUIDField(write_only=True)
    speed = serializers.FloatField(min_value=ALLOWED_MIN_WINDSPEED, max_value=ALLOWED_MAX_WINDSPEED)

    def create(self, validated_data):
        anemometer_id = validated_data.pop('anemometer_id')
        try:
            anemometer = Anemometer.objects.get(id=anemometer_id)
        except Anemometer.DoesNotExist:
            raise serializers.ValidationError(
                {'anemometer_id': 'No anemometer with the given id found.'}
            )
        return WindReading.objects.create(
            anemometer=anemometer,
            **validated_data,
        )

    class Meta:
        model = WindReading
        fields = [
            "anemometer_id",
            "speed",
        ]
        list_serializer_class = BulkWindreadingSerializer

class CreateNestedWindReadingSerializer(serializers.ModelSerializer):
    speed = serializers.FloatField(min_value=ALLOWED_MIN_WINDSPEED, max_value=ALLOWED_MAX_WINDSPEED)

    def validate(self, attrs):
        anemometer_id = self.context['anemometer_id']
        try:
            Anemometer.objects.get(id=anemometer_id)
        except Anemometer.DoesNotExist:
            raise serializers.ValidationError(
                {'anemometer_id': 'No anemometer with the given id found.'}
            )
        return super().validate(attrs)

    def create(self, validated_data):
        anemometer_id = self.context['anemometer_id']
        anemometer = Anemometer.objects.get(id=anemometer_id)
        return WindReading.objects.create(
            anemometer=anemometer,
            **validated_data,
        )
        

    class Meta:
        model = WindReading
        fields = [
            "speed"
        ]