from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Route, Point
from .serializers import RouteSerializer, PointSerializer
from django.db.models import Max

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Route):
            return obj.user == request.user
        elif isinstance(obj, Point):
            return obj.route.user == request.user
        return False

class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Route.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PointViewSet(viewsets.ModelViewSet):
    serializer_class = PointSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        route_id = self.kwargs.get('route_id')
        if route_id is None:
            return Point.objects.none()
        return Point.objects.filter(
            route__id=route_id,
            route__user=self.request.user
        )

    def perform_create(self, serializer):
        route = Route.objects.get(
            id=self.kwargs.get('route_id'),
            user=self.request.user
        )
        last_order = route.points.aggregate(Max('order'))['order__max'] or 0
        serializer.save(route=route, order=last_order + 1)
