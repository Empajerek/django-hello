from rest_framework import serializers
from ..models import Route, Point

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'x', 'y', 'order']
        read_only_fields = ['id', 'order']

class RouteSerializer(serializers.ModelSerializer):
    points = PointSerializer(many=True, read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Route
        fields = ['id', 'name', 'background', 'user', 'points', 'created_at']
        read_only_fields = ['id', 'created_at']
