
from django.urls import path, include, re_path
from irms_app import views
from django.views.static import serve
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'local-data', views.LocalDataEntryViewSet)

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home', views.home, name="home"),
    path('pid_data/', views.pid_data, name="pid_data"),
    path('report', views.report, name="report"),
    path('create/', views.create_user, name='create_user'),
    path('api/', include(router.urls), name="route_urls"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root' : settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$',serve,{'document_root' : settings.STATIC_ROOT}),
]