from django.db import models
import uuid


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Anemometer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, related_name="anemometers", blank=True)

    def __str__(self):
        return self.name

class WindReading(models.Model):
    anemometer = models.ForeignKey(Anemometer, on_delete=models.PROTECT, related_name="wind_readings")
    speed = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.speed} ({self.timestamp}) @ {self.anemometer}"

    class Meta:
        ordering = ["-timestamp"]