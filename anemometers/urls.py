from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register("anemometers", views.AnemometerViewSet, basename="anemometers")
router.register("readings", views.WindReadingViewSet) # all windreadings
router.register("tags", views.TagViewSet) 

anemometers_router = routers.NestedDefaultRouter(
    router, 'anemometers', lookup='anemometer'
)
anemometers_router.register('readings', views.NestedWindReadingViewSet, basename="anemometer-readings")
anemometers_router.register(
    'bulk-wind-readings',
    views.NestedBulkReadingViewSet,
    basename='anemometer-bulk-readings'
)

urlpatterns = router.urls + anemometers_router.urls