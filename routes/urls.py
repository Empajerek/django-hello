from django.urls import path
from django.views.generic.base import RedirectView
from . import views
from rest_framework import permissions
from django.contrib.auth import views as auth_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.views import obtain_auth_token
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
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('api/', include('routes.api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', RedirectView.as_view(url='routes/', permanent=False), name='index'),
]
