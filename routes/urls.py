from django.views.generic.base import RedirectView
from . import views
from django.contrib.auth import views as auth_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.urls import path, include

schema_view = get_schema_view(
    openapi.Info(
      title="Route Editor API",
      default_version='v1',
    ),
    public=False,
    authentication_classes=[SessionAuthentication, BasicAuthentication],
)

urlpatterns = [
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('routes/', views.route_list, name='route_list'),
    path('routes/create/', views.create_route, name='create_route'),
    path('routes/<int:route_id>/', views.route_detail, name='route_detail'),
    path('routes/<int:route_id>/delete_point/<int:point_id>/', views.delete_point, name='delete_point'),

    path('gameboard/', views.gameboard_list, name='gameboard_list'),
    path('gameboard/create/', views.create_gameboard, name='create_gameboard'),
    path('gameboard/<int:gameboard_id>/', views.gameboard_detail, name='gameboard_detail'),
    path('gameboard/<int:gameboard_id>/delete_gameboard', views.delete_gameboard, name='delete_gameboard'),

    path('game/', views.game_list, name='game_list'),
    path('game/create/', views.create_game, name='create_game'),
    path('game/<int:game_id>/', views.play_game, name='play_game'),
    path('game/<int:game_id>/delete', views.delete_game, name='delete_game'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('api/', include('routes.api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', RedirectView.as_view(url='game/', permanent=False), name='index'),
]
