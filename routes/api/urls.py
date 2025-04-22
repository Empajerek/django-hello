from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, PointViewSet

router = DefaultRouter()
router.register(r'routes', RouteViewSet, basename='route')

urlpatterns = [
    path('', include(router.urls)),
    path('routes/<int:route_id>/points/',
         PointViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='route-points'),
    path('routes/<int:route_id>/points/<int:pk>/',
         PointViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
         name='route-point-detail'),
]
