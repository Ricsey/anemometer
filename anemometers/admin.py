from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Anemometer, WindReading, Tag

admin.site.register(Anemometer)
admin.site.register(WindReading)
admin.site.register(Tag)
